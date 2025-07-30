# sage_setup: distribution = sagemath-categories


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from sage.misc.lazy_import import lazy_import
lazy_import('sage.sets.real_set', 'RealSet')
from sage.sets.set import Set
from sage.sets.integer_range import IntegerRange
from sage.sets.non_negative_integers import NonNegativeIntegers
from sage.sets.positive_integers import PositiveIntegers
from sage.sets.finite_enumerated_set import FiniteEnumeratedSet
lazy_import('sage.sets.recursively_enumerated_set', 'RecursivelyEnumeratedSet')
from sage.sets.totally_ordered_finite_set import TotallyOrderedFiniteSet
from sage.sets.disjoint_union_enumerated_sets import DisjointUnionEnumeratedSets
from sage.sets.primes import Primes
from sage.sets.family import Family
from sage.sets.disjoint_set import DisjointSet
from sage.sets.condition_set import ConditionSet
from sage.sets.finite_set_maps import FiniteSetMaps
del lazy_import
