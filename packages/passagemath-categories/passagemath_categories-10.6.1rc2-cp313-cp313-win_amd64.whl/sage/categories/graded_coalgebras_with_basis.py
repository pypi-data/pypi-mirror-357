# sage_setup: distribution = sagemath-categories
r"""
Graded coalgebras with basis
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
#                2019 Travis Scrimshaw <tcscrims at gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.cachefunc import cached_method
from sage.categories.graded_modules import GradedModulesCategory
from sage.categories.signed_tensor import SignedTensorProductsCategory


class GradedCoalgebrasWithBasis(GradedModulesCategory):
    """
    The category of graded coalgebras with a distinguished basis.

    EXAMPLES::

        sage: C = GradedCoalgebrasWithBasis(QQ); C
        Category of graded coalgebras with basis over Rational Field
        sage: C is Coalgebras(QQ).WithBasis().Graded()
        True

    TESTS::

        sage: TestSuite(C).run()
    """
    class SignedTensorProducts(SignedTensorProductsCategory):
        """
        The category of coalgebras with basis constructed by signed tensor
        product of coalgebras with basis.
        """
        @cached_method
        def extra_super_categories(self):
            """
            EXAMPLES::

                sage: Cat = CoalgebrasWithBasis(QQ).Graded()
                sage: Cat.SignedTensorProducts().extra_super_categories()
                [Category of graded coalgebras with basis over Rational Field]
                sage: Cat.SignedTensorProducts().super_categories()
                [Category of graded coalgebras with basis over Rational Field,
                 Category of signed tensor products of graded coalgebras over Rational Field]
            """
            return [self.base_category()]