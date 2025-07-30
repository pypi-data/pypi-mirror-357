# sage_setup: distribution = sagemath-categories
r"""
Gcd domains
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
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.categories.category_singleton import Category_singleton
from sage.categories.integral_domains import IntegralDomains


class GcdDomains(Category_singleton):
    """
    The category of gcd domains
    domains where gcd can be computed but where there is no guarantee of
    factorisation into irreducibles

    EXAMPLES::

        sage: GcdDomains()
        Category of gcd domains
        sage: GcdDomains().super_categories()
        [Category of integral domains]

    TESTS::

        sage: TestSuite(GcdDomains()).run()
    """

    def super_categories(self):
        """
        EXAMPLES::

            sage: GcdDomains().super_categories()
            [Category of integral domains]
        """
        return [IntegralDomains()]

    def additional_structure(self):
        """
        Return ``None``.

        Indeed, the category of gcd domains defines no additional
        structure: a ring morphism between two gcd domains is a gcd
        domain morphism.

        .. SEEALSO:: :meth:`Category.additional_structure`

        EXAMPLES::

            sage: GcdDomains().additional_structure()
        """
        return None

    class ParentMethods:
        pass

    class ElementMethods:
        # gcd(x,y)
        # lcm(x,y)
        pass