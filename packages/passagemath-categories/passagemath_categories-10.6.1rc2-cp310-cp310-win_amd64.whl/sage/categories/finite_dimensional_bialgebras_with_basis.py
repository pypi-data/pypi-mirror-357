# sage_setup: distribution = sagemath-categories
r"""
Finite dimensional bialgebras with basis
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
#                2011 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************


def FiniteDimensionalBialgebrasWithBasis(base_ring):
    """
    The category of finite dimensional bialgebras with a distinguished basis.

    EXAMPLES::

        sage: C = FiniteDimensionalBialgebrasWithBasis(QQ); C
        Category of finite dimensional bialgebras with basis over Rational Field
        sage: sorted(C.super_categories(), key=str)
        [Category of bialgebras with basis over Rational Field,
         Category of finite dimensional algebras with basis over Rational Field]
        sage: C is Bialgebras(QQ).WithBasis().FiniteDimensional()
        True

    TESTS::

        sage: TestSuite(C).run()
    """
    from sage.categories.bialgebras_with_basis import BialgebrasWithBasis
    return BialgebrasWithBasis(base_ring).FiniteDimensional()