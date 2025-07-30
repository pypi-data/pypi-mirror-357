# sage_setup: distribution = sagemath-categories
r"""
Semirings
"""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

# ****************************************************************************
#  Copyright (C) 2010 Nicolas Borie <nicolas.borie@math.u-psud.fr>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  https://www.gnu.org/licenses/
# *****************************************************************************

from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.categories.magmas_and_additive_magmas import MagmasAndAdditiveMagmas


class Semirings(CategoryWithAxiom):
    """
    The category of semirings.

    A semiring `(S, +, *)` is similar to a ring, but without the
    requirement that each element must have an additive inverse. In
    other words, it is a combination of a commutative additive monoid
    `(S, +)` and a multiplicative monoid `(S, *)`, where `*` distributes
    over `+`.

    .. SEEALSO::

        :wikipedia:`Semiring`

    EXAMPLES::

        sage: Semirings()
        Category of semirings
        sage: Semirings().super_categories()
        [Category of associative additive commutative additive
         associative additive unital distributive magmas and additive magmas,
         Category of monoids]

        sage: sorted(Semirings().axioms())
        ['AdditiveAssociative', 'AdditiveCommutative', 'AdditiveUnital',
         'Associative', 'Distributive', 'Unital']

        sage: Semirings() is (CommutativeAdditiveMonoids() & Monoids()).Distributive()
        True

        sage: Semirings().AdditiveInverse()
        Category of rings


    TESTS::

        sage: TestSuite(Semirings()).run()
        sage: Semirings().example()
        An example of a semiring: the ternary-logic semiring
    """
    _base_category_class_and_axiom = (MagmasAndAdditiveMagmas.Distributive.AdditiveAssociative.AdditiveCommutative.AdditiveUnital.Associative, "Unital")

    def __lean_init__(self):
        r"""
        Return the category as Lean mathlib input for a typeclass.

        EXAMPLES::

            sage: from sage.categories.semirings import Semirings
            sage: C = Semirings(); C
            Category of semirings
            sage: C.__lean_init__()
            'semiring'
        """
        # defined in algebra.ring.basic
        return 'semiring'