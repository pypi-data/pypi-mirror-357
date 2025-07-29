/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use std::cell::RefCell;
use std::fmt;
use std::fmt::Debug;
use std::fmt::Display;
use std::path::PathBuf;
use std::sync::Arc;

use dupe::Dupe;
use dupe::OptionDupedExt;
use pyrefly_util::display::DisplayWith;
use pyrefly_util::display::DisplayWithCtx;
use pyrefly_util::gas::Gas;
use pyrefly_util::lock::Mutex;
use pyrefly_util::recurser::Recurser;
use pyrefly_util::uniques::UniqueFactory;
use pyrefly_util::visit::VisitMut;
use ruff_python_ast::name::Name;
use ruff_text_size::Ranged;
use ruff_text_size::TextRange;
use starlark_map::Hashed;
use starlark_map::small_map::SmallMap;
use starlark_map::small_set::SmallSet;
use vec1::vec1;

use crate::alt::attr::AttrDefinition;
use crate::alt::attr::AttrInfo;
use crate::alt::traits::Solve;
use crate::alt::traits::SolveRecursive;
use crate::binding::binding::AnyIdx;
use crate::binding::binding::Binding;
use crate::binding::binding::Exported;
use crate::binding::binding::Key;
use crate::binding::binding::Keyed;
use crate::binding::bindings::BindingEntry;
use crate::binding::bindings::BindingTable;
use crate::binding::bindings::Bindings;
use crate::binding::table::TableKeyed;
use crate::error::collector::ErrorCollector;
use crate::error::context::ErrorContext;
use crate::error::context::TypeCheckContext;
use crate::error::kind::ErrorKind;
use crate::error::style::ErrorStyle;
use crate::export::exports::LookupExport;
use crate::graph::calculation::Calculation;
use crate::graph::index::Idx;
use crate::graph::index_map::IndexMap;
use crate::module::module_info::ModuleInfo;
use crate::module::module_info::TextRangeWithModuleInfo;
use crate::module::module_name::ModuleName;
use crate::module::module_path::ModulePath;
use crate::solver::solver::Solver;
use crate::solver::type_order::TypeOrder;
use crate::state::ide::IntermediateDefinition;
use crate::state::ide::binding_to_intermediate_definition;
use crate::table;
use crate::table_for_each;
use crate::table_mut_for_each;
use crate::table_try_for_each;
use crate::types::callable::Callable;
use crate::types::class::Class;
use crate::types::equality::TypeEq;
use crate::types::equality::TypeEqCtx;
use crate::types::stdlib::Stdlib;
use crate::types::type_info::TypeInfo;
use crate::types::types::Type;
use crate::types::types::Var;

/// The index stores all the references where the definition is external to the current module.
/// This is useful for fast references computation.
#[derive(Debug, Default)]
pub struct Index {
    /// A map from (import specifier (ModuleName), imported symbol (Name)) to all references to it
    /// in the current module.
    pub externally_defined_variable_references: SmallMap<(ModuleName, Name), Vec<TextRange>>,
    /// A map from (attribute definition module) to a list of pairs of
    /// (range of attribute definition in the definition, range of reference in the current module).
    pub externally_defined_attribute_references: SmallMap<ModulePath, Vec<(TextRange, TextRange)>>,
}

#[derive(Debug)]
struct OverloadedCallee {
    all_overloads: Vec<Callable>,
    closest_overload: Callable,
    is_closest_overload_chosen: bool,
}

#[derive(Debug, Default)]
pub struct Traces {
    types: SmallMap<TextRange, Arc<Type>>,
    /// A map from (range of callee, overload information)
    overloaded_callees: SmallMap<TextRange, OverloadedCallee>,
}

/// Invariants:
///
/// * Every module name referenced anywhere MUST be present
///   in the `exports` and `bindings` map.
/// * Every key referenced in `bindings`/`answers` MUST be present.
///
/// We never issue contains queries on these maps.
#[derive(Debug)]
pub struct Answers {
    solver: Solver,
    table: AnswerTable,
    index: Option<Arc<Mutex<Index>>>,
    trace: Option<Mutex<Traces>>,
}

pub type AnswerEntry<K> =
    IndexMap<K, Calculation<Arc<<K as Keyed>::Answer>, <K as SolveRecursive>::Recursive>>;

table!(
    #[derive(Debug, Default)]
    pub struct AnswerTable(pub AnswerEntry)
);

impl DisplayWith<Bindings> for Answers {
    fn fmt(&self, f: &mut fmt::Formatter<'_>, bindings: &Bindings) -> fmt::Result {
        fn go<K: SolveRecursive>(
            bindings: &Bindings,
            entry: &AnswerEntry<K>,
            f: &mut fmt::Formatter<'_>,
        ) -> fmt::Result
        where
            BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
        {
            for (idx, answer) in entry.iter() {
                let key = bindings.idx_to_key(idx);
                let value = bindings.get(idx);
                writeln!(
                    f,
                    "{} = {} = {}",
                    bindings.module_info().display(key),
                    value.display_with(bindings),
                    match answer.get() {
                        Some(v) => v.to_string(),
                        None => "(unsolved)".to_owned(),
                    },
                )?;
            }
            Ok(())
        }

        table_try_for_each!(self.table, |x| go(bindings, x, f));
        Ok(())
    }
}

pub type SolutionsEntry<K> = SmallMap<K, Arc<<K as Keyed>::Answer>>;

table!(
    // Only the exported keys are stored in the solutions table.
    #[derive(Default, Debug, Clone, PartialEq, Eq)]
    pub struct SolutionsTable(pub SolutionsEntry)
);

#[derive(Debug, Clone)]
pub struct Solutions {
    module_info: ModuleInfo,
    table: SolutionsTable,
    index: Option<Arc<Mutex<Index>>>,
}

impl Display for Solutions {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        fn go<K: Keyed>(
            entry: &SolutionsEntry<K>,
            f: &mut fmt::Formatter<'_>,
            ctx: &ModuleInfo,
        ) -> fmt::Result
        where
            BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
        {
            for (key, answer) in entry {
                writeln!(f, "{} = {}", ctx.display(key), answer)?;
            }
            Ok(())
        }

        table_try_for_each!(&self.table, |x| go(x, f, &self.module_info));
        Ok(())
    }
}

pub struct SolutionsDifference<'a> {
    key: (&'a dyn DisplayWith<ModuleInfo>, &'a dyn Debug),
    lhs: Option<(&'a dyn Display, &'a dyn Debug)>,
    rhs: Option<(&'a dyn Display, &'a dyn Debug)>,
}

impl Debug for SolutionsDifference<'_> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("SolutionsDifference")
            .field("key", self.key.1)
            .field("lhs", &self.lhs.map(|x| x.1))
            .field("rhs", &self.rhs.map(|x| x.1))
            .finish()
    }
}

impl Display for SolutionsDifference<'_> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let missing = |f: &mut fmt::Formatter, x: Option<(&dyn Display, &dyn Debug)>| match x {
            None => write!(f, "missing"),
            Some(x) => write!(f, "`{}`", x.0),
        };

        // The key has type DisplayWith<ModuleInfo>.
        // We don't know if the key originates on the LHS or RHS, so we don't know which is the appropriate ModuleInfo.
        // However, we do know it is exported, and exported things can't rely on locations, so regardless
        // of the ModuleInfo, it should display the same. Therefore, we fake one up.
        let fake_module_info = ModuleInfo::new(
            ModuleName::from_str("Fake.Module.For.SolutionsDifference.Display"),
            ModulePath::memory(PathBuf::new()),
            Default::default(),
        );

        write!(f, "`")?;
        self.key.0.fmt(f, &fake_module_info)?;
        write!(f, "` was ")?;
        missing(f, self.lhs)?;
        write!(f, " now ")?;
        missing(f, self.rhs)?;
        Ok(())
    }
}

impl Solutions {
    #[allow(dead_code)] // Used in tests.
    pub fn get<K: Exported>(&self, key: &K) -> &Arc<<K as Keyed>::Answer>
    where
        SolutionsTable: TableKeyed<K, Value = SolutionsEntry<K>>,
    {
        self.get_hashed(Hashed::new(key))
    }

    pub fn get_hashed<K: Exported>(&self, key: Hashed<&K>) -> &Arc<<K as Keyed>::Answer>
    where
        SolutionsTable: TableKeyed<K, Value = SolutionsEntry<K>>,
    {
        self.table.get().get_hashed(key).unwrap_or_else(|| {
            panic!(
                "Internal error: solution not found, module {}, path {}, key {:?}",
                self.module_info.name(),
                self.module_info.path(),
                key.key(),
            )
        })
    }

    /// Find the first key that differs between two solutions, with the two values.
    ///
    /// Don't love that we always allocate String's for the result, but it's rare that
    /// there is a difference, and if there is, we'll do quite a lot of computation anyway.
    pub fn first_difference<'a>(&'a self, other: &'a Self) -> Option<SolutionsDifference<'a>> {
        fn f<'a, K: Keyed>(
            x: &'a SolutionsEntry<K>,
            y: &'a Solutions,
            ctx: &mut TypeEqCtx,
        ) -> Option<SolutionsDifference<'a>>
        where
            SolutionsTable: TableKeyed<K, Value = SolutionsEntry<K>>,
        {
            if !K::EXPORTED {
                assert_eq!(x.len(), 0, "Expect no non-exported keys in Solutions");
                return None;
            }

            let y = y.table.get::<K>();
            if y.len() > x.len() {
                for (k, v) in y {
                    if !x.contains_key(k) {
                        return Some(SolutionsDifference {
                            key: (k, k),
                            lhs: None,
                            rhs: Some((v, v)),
                        });
                    }
                }
                unreachable!();
            }
            for (k, v) in x {
                match y.get(k) {
                    Some(v2) if !v.type_eq(v2, ctx) => {
                        return Some(SolutionsDifference {
                            key: (k, k),
                            lhs: Some((v, v)),
                            rhs: Some((v2, v2)),
                        });
                    }
                    None => {
                        return Some(SolutionsDifference {
                            key: (k, k),
                            lhs: Some((v, v)),
                            rhs: None,
                        });
                    }
                    _ => {}
                }
            }
            None
        }

        let mut difference = None;
        // Important we have a single TypeEqCtx, so that we don't have
        // types used in different ways.
        let mut ctx = TypeEqCtx::default();
        table_for_each!(self.table, |x| {
            if difference.is_none() {
                difference = f(x, other, &mut ctx);
            }
        });
        difference
    }

    pub fn get_index(&self) -> Option<Arc<Mutex<Index>>> {
        let index = self.index.as_ref()?;
        Some(index.dupe())
    }
}

/// Compactly represents the identity of a binding, for the purposes of
/// understanding the calculation stack.
#[derive(Debug, Clone, Dupe)]
pub struct CalcId(pub Bindings, pub AnyIdx);

impl PartialEq for CalcId {
    fn eq(&self, other: &Self) -> bool {
        (self.0.module_info(), &self.1) == (other.0.module_info(), &other.1)
    }
}

/// Represent a stack of in-progress calculations in an `AnswersSolver`.
///
/// This is useful for debugging, particularly for debugging cycle handling.
///
/// The stack is per-thread; we create a new `AnswersSolver` every time
/// we change modules when resolving exports, but the stack is passed
/// down because cycles can cross module boundaries.
pub struct CalcStack(RefCell<Vec<CalcId>>);

impl CalcStack {
    pub fn new() -> Self {
        Self(RefCell::new(Vec::new()))
    }

    fn push(&self, bindings: Bindings, idx: AnyIdx) {
        self.0.borrow_mut().push(CalcId(bindings, idx));
    }

    fn pop(&self) -> Option<CalcId> {
        self.0.borrow_mut().pop()
    }

    pub fn peek(&self) -> Option<CalcId> {
        self.0.borrow().last().cloned()
    }

    pub fn into_vec(&self) -> Vec<CalcId> {
        self.0.borrow().clone()
    }
}

pub struct AnswersSolver<'a, Ans: LookupAnswer> {
    answers: &'a Ans,
    current: &'a Answers,
    stack: &'a CalcStack,
    // The base solver is only used to reset the error collector at binding
    // boundaries. Answers code should generally use the error collector passed
    // along the call stack instead.
    base_errors: &'a ErrorCollector,
    bindings: &'a Bindings,
    pub exports: &'a dyn LookupExport,
    pub uniques: &'a UniqueFactory,
    pub recurser: &'a Recurser<Var>,
    pub stdlib: &'a Stdlib,
}

pub trait LookupAnswer: Sized {
    fn get<K: Solve<Self> + Exported>(
        &self,
        module: ModuleName,
        path: Option<&ModulePath>,
        k: &K,
        stack: &CalcStack,
    ) -> Arc<K::Answer>
    where
        AnswerTable: TableKeyed<K, Value = AnswerEntry<K>>,
        BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
        SolutionsTable: TableKeyed<K, Value = SolutionsEntry<K>>;
}

impl Answers {
    pub fn table(&self) -> &AnswerTable {
        &self.table
    }

    pub fn new(
        bindings: &Bindings,
        solver: Solver,
        enable_index: bool,
        enable_trace: bool,
    ) -> Self {
        fn presize<K: SolveRecursive>(items: &mut AnswerEntry<K>, bindings: &Bindings)
        where
            BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
        {
            let ks = bindings.keys::<K>();
            items.reserve(ks.len());
            for k in ks {
                items.insert_once(k, Calculation::new());
            }
        }
        let mut table = AnswerTable::default();
        table_mut_for_each!(&mut table, |items| presize(items, bindings));
        let index = if enable_index {
            Some(Arc::new(Mutex::new(Index::default())))
        } else {
            None
        };
        let trace = if enable_trace {
            Some(Mutex::new(Traces::default()))
        } else {
            None
        };

        Self {
            solver,
            table,
            index,
            trace,
        }
    }

    #[expect(dead_code)]
    fn len(&self) -> usize {
        let mut res = 0;
        table_for_each!(&self.table, |x: &AnswerEntry<_>| res += x.len());
        res
    }

    pub fn solve<Ans: LookupAnswer>(
        &self,
        exports: &dyn LookupExport,
        answers: &Ans,
        bindings: &Bindings,
        errors: &ErrorCollector,
        stdlib: &Stdlib,
        uniques: &UniqueFactory,
        compute_everything: bool,
    ) -> Solutions {
        let mut res = SolutionsTable::default();

        fn pre_solve<Ans: LookupAnswer, K: Solve<Ans>>(
            items: &mut SolutionsEntry<K>,
            answers: &AnswersSolver<Ans>,
            compute_everything: bool,
        ) where
            AnswerTable: TableKeyed<K, Value = AnswerEntry<K>>,
            BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
        {
            if K::EXPORTED {
                items.reserve(answers.bindings.keys::<K>().len());
            }
            if !K::EXPORTED
                && !compute_everything
                && answers.base_errors.style() == ErrorStyle::Never
            {
                // No point doing anything here.
                return;
            }
            for idx in answers.bindings.keys::<K>() {
                let v = answers.get_idx(idx);
                if K::EXPORTED {
                    let k = answers.bindings.idx_to_key(idx);
                    items.insert(k.clone(), v.dupe());
                }
            }
        }
        let answers_solver = AnswersSolver {
            stdlib,
            answers,
            stack: &CalcStack::new(),
            bindings,
            base_errors: errors,
            exports,
            uniques,
            recurser: &Recurser::new(),
            current: self,
        };
        table_mut_for_each!(&mut res, |items| pre_solve(
            items,
            &answers_solver,
            compute_everything
        ));
        if let Some(index) = &self.index {
            let mut index = index.lock();
            // Index bindings with external definitions.
            for idx in bindings.keys::<Key>() {
                let binding = bindings.get(idx);
                let (imported_module_name, imported_name) = match binding_to_intermediate_definition(
                    bindings,
                    binding,
                    &mut Gas::new(20),
                ) {
                    None => continue,
                    Some(IntermediateDefinition::Local(_)) => continue,
                    Some(IntermediateDefinition::Module(_)) => continue,
                    Some(IntermediateDefinition::NamedImport(module_name, name)) => {
                        (module_name, name)
                    }
                };
                let reference_range = bindings.idx_to_key(idx).range();
                // Sanity check: the reference should have the same text as the definition.
                // This check helps to filter out synthetic bindings.
                if bindings.module_info().code_at(reference_range) == imported_name.as_str() {
                    index
                        .externally_defined_variable_references
                        .entry((imported_module_name, imported_name))
                        .or_default()
                        .push(reference_range);
                }
            }
        }

        // Now force all types to be fully resolved.
        fn post_solve<K: Keyed>(items: &mut SolutionsEntry<K>, solver: &Solver) {
            for v in items.values_mut() {
                let mut vv = (**v).clone();
                vv.visit_mut(&mut |x| solver.deep_force_mut(x));
                *v = Arc::new(vv);
            }
        }
        table_mut_for_each!(&mut res, |items| post_solve(items, &self.solver));
        Solutions {
            module_info: bindings.module_info().dupe(),
            table: res,
            index: self.index.dupe(),
        }
    }

    pub fn solve_exported_key<Ans: LookupAnswer, K: Solve<Ans> + Exported>(
        &self,
        exports: &dyn LookupExport,
        answers: &Ans,
        bindings: &Bindings,
        errors: &ErrorCollector,
        stdlib: &Stdlib,
        uniques: &UniqueFactory,
        key: Hashed<&K>,
        stack: &CalcStack,
    ) -> Arc<K::Answer>
    where
        AnswerTable: TableKeyed<K, Value = AnswerEntry<K>>,
        BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
    {
        let solver = AnswersSolver {
            stdlib,
            uniques,
            answers,
            bindings,
            base_errors: errors,
            exports,
            recurser: &Recurser::new(),
            current: self,
            stack,
        };
        let v = solver.get_hashed(key);
        let mut vv = (*v).clone();
        vv.visit_mut(&mut |x| self.solver.deep_force_mut(x));
        Arc::new(vv)
    }

    pub fn get_idx<K: SolveRecursive>(&self, k: Idx<K>) -> Option<Arc<K::Answer>>
    where
        AnswerTable: TableKeyed<K, Value = AnswerEntry<K>>,
    {
        self.table.get::<K>().get(k)?.get()
    }

    pub fn for_display(&self, t: Type) -> Type {
        self.solver.for_display(t)
    }

    pub fn solver(&self) -> &Solver {
        &self.solver
    }

    pub fn get_type_trace(&self, range: TextRange) -> Option<Arc<Type>> {
        let lock = self.trace.as_ref()?.lock();
        lock.types.get(&range).duped()
    }

    pub fn get_chosen_overload_trace(&self, range: TextRange) -> Option<Callable> {
        let lock = self.trace.as_ref()?.lock();
        let overloaded_callee = lock.overloaded_callees.get(&range)?;
        if overloaded_callee.is_closest_overload_chosen {
            Some(overloaded_callee.closest_overload.clone())
        } else {
            None
        }
    }

    /// Returns all the overload, and the index of a chosen one
    pub fn get_all_overload_trace(
        &self,
        range: TextRange,
    ) -> Option<(Vec<Callable>, Option<usize>)> {
        let lock = self.trace.as_ref()?.lock();
        let overloaded_callee = lock.overloaded_callees.get(&range)?;
        let chosen_overload_index =
            overloaded_callee
                .all_overloads
                .iter()
                .enumerate()
                .find_map(|(index, signature)| {
                    if signature == &overloaded_callee.closest_overload {
                        Some(index)
                    } else {
                        None
                    }
                });
        Some((
            overloaded_callee.all_overloads.clone(),
            chosen_overload_index,
        ))
    }
}

impl<'a, Ans: LookupAnswer> AnswersSolver<'a, Ans> {
    pub fn new(
        answers: &'a Ans,
        current: &'a Answers,
        base_errors: &'a ErrorCollector,
        bindings: &'a Bindings,
        exports: &'a dyn LookupExport,
        uniques: &'a UniqueFactory,
        recurser: &'a Recurser<Var>,
        stdlib: &'a Stdlib,
        stack: &'a CalcStack,
    ) -> AnswersSolver<'a, Ans> {
        AnswersSolver {
            stdlib,
            uniques,
            answers,
            bindings,
            base_errors,
            exports,
            recurser,
            current,
            stack,
        }
    }

    pub fn bindings(&self) -> &Bindings {
        self.bindings
    }

    pub fn module_info(&self) -> &ModuleInfo {
        self.bindings.module_info()
    }

    pub fn solver(&self) -> &Solver {
        &self.current.solver
    }

    pub fn stack(&self) -> &CalcStack {
        self.stack
    }

    pub fn for_display(&self, t: Type) -> Type {
        self.solver().for_display(t)
    }

    pub fn get_from_module<K: Solve<Ans> + Exported>(
        &self,
        module: ModuleName,
        path: Option<&ModulePath>,
        k: &K,
    ) -> Arc<K::Answer>
    where
        AnswerTable: TableKeyed<K, Value = AnswerEntry<K>>,
        BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
        SolutionsTable: TableKeyed<K, Value = SolutionsEntry<K>>,
    {
        if module == self.module_info().name()
            && path.is_none_or(|path| path == self.module_info().path())
        {
            self.get(k)
        } else {
            self.answers.get(module, path, k, self.stack)
        }
    }

    pub fn get_from_class<K: Solve<Ans> + Exported>(&self, cls: &Class, k: &K) -> Arc<K::Answer>
    where
        AnswerTable: TableKeyed<K, Value = AnswerEntry<K>>,
        BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
        SolutionsTable: TableKeyed<K, Value = SolutionsEntry<K>>,
    {
        self.get_from_module(cls.module_name(), Some(cls.module_info().path()), k)
    }

    pub fn type_order(&self) -> TypeOrder<Ans> {
        TypeOrder::new(self)
    }

    fn get_calculation<K: Solve<Ans>>(
        &self,
        idx: Idx<K>,
    ) -> &Calculation<Arc<K::Answer>, K::Recursive>
    where
        AnswerTable: TableKeyed<K, Value = AnswerEntry<K>>,
        BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
    {
        self.current.table.get::<K>().get(idx).unwrap_or_else(|| {
            // Do not fix a panic by removing this error.
            // We should always be sure before calling `get`.
            panic!(
                "Internal error: answer not found, module {}, path {}, key {:?}",
                self.module_info().name(),
                self.module_info().path(),
                self.bindings().idx_to_key(idx),
            )
        })
    }

    pub fn get_idx<K: Solve<Ans>>(&self, idx: Idx<K>) -> Arc<K::Answer>
    where
        AnswerTable: TableKeyed<K, Value = AnswerEntry<K>>,
        BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
    {
        let calculation = self.get_calculation(idx);
        self.stack.push(self.bindings().dupe(), K::to_anyidx(idx));
        let result = calculation.calculate_with_recursive(
            || {
                let binding = self.bindings().get(idx);
                K::solve(self, binding, self.base_errors)
            },
            || {
                let binding = self.bindings().get(idx);
                K::create_recursive(self, binding)
            },
        );
        if let Ok((v, Some(r))) = &result {
            let k = self.bindings().idx_to_key(idx).range();
            K::record_recursive(self, k, v, r, self.base_errors);
        }
        self.stack.pop();
        match result {
            Ok((v, _)) => v,
            Err(r) => Arc::new(K::promote_recursive(r)),
        }
    }

    pub fn get<K: Solve<Ans>>(&self, k: &K) -> Arc<K::Answer>
    where
        AnswerTable: TableKeyed<K, Value = AnswerEntry<K>>,
        BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
    {
        self.get_hashed(Hashed::new(k))
    }

    pub fn get_hashed<K: Solve<Ans>>(&self, k: Hashed<&K>) -> Arc<K::Answer>
    where
        AnswerTable: TableKeyed<K, Value = AnswerEntry<K>>,
        BindingTable: TableKeyed<K, Value = BindingEntry<K>>,
    {
        self.get_idx(self.bindings().key_to_idx_hashed(k))
    }

    pub fn create_recursive(&self, binding: &Binding) -> Var {
        let t = if let Binding::Default(default, _) = binding {
            self.get_calculation(*default)
                .get()
                .map(|t| t.arc_clone_ty().promote_literals(self.stdlib))
        } else {
            None
        };
        self.solver().fresh_recursive(self.uniques, t)
    }

    pub fn record_recursive(
        &self,
        loc: TextRange,
        answer: Type,
        recursive: Var,
        errors: &ErrorCollector,
    ) {
        self.solver()
            .record_recursive(recursive, answer, self.type_order(), errors, loc);
    }

    pub fn record_type_trace(&self, loc: TextRange, ty: &Type) {
        if let Some(trace) = &self.current.trace {
            trace.lock().types.insert(loc, Arc::new(ty.clone()));
        }
    }

    /// Record all the overloads and the chosen overload.
    /// The trace will be used to power signature help and hover for overloaded functions.
    pub fn record_overload_trace(
        &self,
        loc: TextRange,
        all_overloads: &[Callable],
        closest_overload: &Callable,
        is_closest_overload_chosen: bool,
    ) {
        if let Some(trace) = &self.current.trace {
            trace.lock().overloaded_callees.insert(
                loc,
                OverloadedCallee {
                    all_overloads: all_overloads.to_vec(),
                    closest_overload: closest_overload.clone(),
                    is_closest_overload_chosen,
                },
            );
        }
    }

    /// Check if `want` matches `got` returning `want` if the check fails.
    pub fn check_and_return_type_info(
        &self,
        want: &Type,
        got: TypeInfo,
        loc: TextRange,
        errors: &ErrorCollector,
        tcc: &dyn Fn() -> TypeCheckContext,
    ) -> TypeInfo {
        if self.check_type(want, got.ty(), loc, errors, tcc) {
            got
        } else {
            got.with_ty(want.clone())
        }
    }

    /// Check if `want` matches `got` returning `want` if the check fails.
    pub fn check_and_return_type(
        &self,
        want: &Type,
        got: Type,
        loc: TextRange,
        errors: &ErrorCollector,
        tcc: &dyn Fn() -> TypeCheckContext,
    ) -> Type {
        if self.check_type(want, &got, loc, errors, tcc) {
            got
        } else {
            want.clone()
        }
    }

    /// Check if `want` matches `got`, returning `true` on success and `false` on failure.
    pub fn check_type(
        &self,
        want: &Type,
        got: &Type,
        loc: TextRange,
        errors: &ErrorCollector,
        tcc: &dyn Fn() -> TypeCheckContext,
    ) -> bool {
        if got.is_error() || self.is_subset_eq(got, want) {
            true
        } else {
            self.solver().error(want, got, errors, loc, tcc);
            false
        }
    }

    pub fn distribute_over_union(&self, ty: &Type, mut f: impl FnMut(&Type) -> Type) -> Type {
        let mut res = Vec::new();
        self.map_over_union(ty, |ty| {
            res.push(f(ty));
        });
        self.unions(res)
    }

    pub fn map_over_union(&self, ty: &Type, f: impl FnMut(&Type)) {
        struct Data<'a, 'b, Ans: LookupAnswer, F: FnMut(&Type)> {
            /// The `self` of `AnswersSolver`
            me: &'b AnswersSolver<'a, Ans>,
            /// The function to apply on each call
            f: F,
            /// Arguments we have already used for the function.
            /// If we see the same element twice in a union (perhaps due to nested Var expansion),
            /// we only need to process it once. Avoids O(n^2) for certain flow patterns.
            done: SmallSet<Type>,
            /// Have we seen a union node? If not, we can skip the cache
            /// as there will only be exactly one call to `f` (the common case).
            seen_union: bool,
        }

        impl<Ans: LookupAnswer, F: FnMut(&Type)> Data<'_, '_, Ans, F> {
            fn go(&mut self, ty: &Type, in_type: bool) {
                match ty {
                    Type::Never(_) if !in_type => (),
                    Type::Union(tys) => {
                        self.seen_union = true;
                        tys.iter().for_each(|ty| self.go(ty, in_type))
                    }
                    Type::Type(box Type::Union(tys)) if !in_type => {
                        tys.iter().for_each(|ty| self.go(ty, true))
                    }
                    Type::Var(v) if let Some(_guard) = self.me.recurser.recurse(*v) => {
                        self.go(&self.me.solver().force_var(*v), in_type)
                    }
                    _ if in_type => (self.f)(&Type::Type(Box::new(ty.clone()))),
                    _ => {
                        // If we haven't encountered a union this must be the only type, no need to cache it.
                        // Otherwise, if inserting succeeds (we haven't processed this type before) actually do it.
                        if !self.seen_union || self.done.insert(ty.clone()) {
                            (self.f)(ty)
                        }
                    }
                }
            }
        }
        Data {
            me: self,
            f,
            done: SmallSet::new(),
            seen_union: false,
        }
        .go(ty, false)
    }

    pub fn unions(&self, xs: Vec<Type>) -> Type {
        self.solver().unions(xs, self.type_order())
    }

    pub fn union(&self, x: Type, y: Type) -> Type {
        self.unions(vec![x, y])
    }

    pub fn error(
        &self,
        errors: &ErrorCollector,
        range: TextRange,
        kind: ErrorKind,
        context: Option<&dyn Fn() -> ErrorContext>,
        msg: String,
    ) -> Type {
        errors.add(range, kind, context, vec1![msg]);
        Type::any_error()
    }

    /// Create a new error collector. Useful when a caller wants to decide whether or not to report
    /// errors from an operation.
    pub fn error_collector(&self) -> ErrorCollector {
        ErrorCollector::new(self.module_info().dupe(), ErrorStyle::Delayed)
    }

    /// Create an error collector that simply swallows errors. Useful when a caller wants to try an
    /// operation that may error but never report errors from it.
    pub fn error_swallower(&self) -> ErrorCollector {
        ErrorCollector::new(self.module_info().dupe(), ErrorStyle::Never)
    }

    pub fn record_external_attribute_definition_index(
        &self,
        base: &Type,
        attribute_name: &Name,
        attribute_reference_range: TextRange,
    ) {
        if let Some(index) = &self.current.index {
            for AttrInfo {
                name: _,
                ty: _,
                definition,
            } in self.completions(base.clone(), Some(attribute_name), false)
            {
                match definition {
                    Some(AttrDefinition::FullyResolved(TextRangeWithModuleInfo {
                        module_info: module,
                        range,
                    })) => {
                        if module.path() != self.bindings().module_info().path() {
                            index
                                .lock()
                                .externally_defined_attribute_references
                                .entry(module.path().dupe())
                                .or_default()
                                .push((range, attribute_reference_range))
                        }
                    }
                    Some(AttrDefinition::PartiallyResolvedImportedModuleAttribute {
                        module_name,
                    }) => {
                        index
                            .lock()
                            .externally_defined_variable_references
                            .entry((module_name, attribute_name.clone()))
                            .or_default()
                            .push(attribute_reference_range);
                    }
                    None => {}
                }
            }
        }
    }
}
