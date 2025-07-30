# sage_setup: distribution = sagemath-categories
r"""
Finite dimensional Hopf algebras with basis
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
#  Copyright (C) 2008 Teresa Gomez-Diaz (CNRS) <Teresa.Gomez-Diaz@univ-mlv.fr>
#                2011 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  https://www.gnu.org/licenses/
# *****************************************************************************

from sage.categories.category_with_axiom import CategoryWithAxiom_over_base_ring


class FiniteDimensionalHopfAlgebrasWithBasis(CategoryWithAxiom_over_base_ring):
    """
    The category of finite dimensional Hopf algebras with a
    distinguished basis.

    EXAMPLES::

        sage: FiniteDimensionalHopfAlgebrasWithBasis(QQ)
        Category of finite dimensional Hopf algebras with basis over Rational Field
        sage: FiniteDimensionalHopfAlgebrasWithBasis(QQ).super_categories()
        [Category of Hopf algebras with basis over Rational Field,
         Category of finite dimensional algebras with basis over Rational Field]

    TESTS::

        sage: TestSuite(FiniteDimensionalHopfAlgebrasWithBasis(ZZ)).run()
    """

    class ParentMethods:
        pass

    class ElementMethods:
        pass