# sage_setup: distribution = sagemath-categories
r"""
Commutative additive monoids
"""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

#*****************************************************************************
#  Copyright (C) 2008 Teresa Gomez-Diaz (CNRS) <Teresa.Gomez-Diaz@univ-mlv.fr>
#                2008-2009 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.categories.additive_monoids import AdditiveMonoids


class CommutativeAdditiveMonoids(CategoryWithAxiom):
    """
    The category of commutative additive monoids, that is abelian
    additive semigroups with a unit

    EXAMPLES::

        sage: C = CommutativeAdditiveMonoids(); C
        Category of commutative additive monoids
        sage: C.super_categories()
        [Category of additive monoids, Category of commutative additive semigroups]
        sage: sorted(C.axioms())
        ['AdditiveAssociative', 'AdditiveCommutative', 'AdditiveUnital']
        sage: C is AdditiveMagmas().AdditiveAssociative().AdditiveCommutative().AdditiveUnital()
        True

    .. NOTE::

        This category is currently empty and only serves as a place
        holder to make ``C.example()`` work.

    TESTS::

        sage: TestSuite(CommutativeAdditiveMonoids()).run()
    """
    _base_category_class_and_axiom = (AdditiveMonoids, "AdditiveCommutative")

    def __lean_init__(self):
        return 'add_comm_monoid'