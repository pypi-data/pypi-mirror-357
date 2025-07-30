# sage_setup: distribution = sagemath-categories
r"""
Matrix algebras
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
#  Copyright (C) 2005      David Kohel <kohel@maths.usyd.edu>
#                          William Stein <wstein@math.ucsd.edu>
#                2008-2009 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.categories.algebras import Algebras
from sage.categories.category_types import Category_over_base_ring


class MatrixAlgebras(Category_over_base_ring):
    """
    The category of matrix algebras over a field.

    EXAMPLES::

        sage: MatrixAlgebras(RationalField())
        Category of matrix algebras over Rational Field

    TESTS::

        sage: TestSuite(MatrixAlgebras(ZZ)).run()
    """

    def super_categories(self):
        """
        EXAMPLES::

            sage: MatrixAlgebras(QQ).super_categories()
            [Category of algebras over Rational Field]
        """
        R = self.base_ring()
        return [Algebras(R)]