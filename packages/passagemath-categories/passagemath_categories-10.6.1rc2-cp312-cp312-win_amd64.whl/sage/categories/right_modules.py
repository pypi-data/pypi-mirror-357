# sage_setup: distribution = sagemath-categories
r"""
Right modules
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

from sage.categories.category_types import Category_over_base_ring
from sage.categories.commutative_additive_groups import CommutativeAdditiveGroups


##?class RightModules(Category_over_base_rng):
class RightModules(Category_over_base_ring):
    """
    The category of right modules
    right modules over an rng (ring not necessarily with unit), i.e.
    an abelian group with right multiplication by elements of the rng

    EXAMPLES::

        sage: RightModules(QQ)
        Category of right modules over Rational Field
        sage: RightModules(QQ).super_categories()
        [Category of commutative additive groups]

    TESTS::

        sage: TestSuite(RightModules(ZZ)).run()
    """

    def super_categories(self):
        """
        EXAMPLES::

            sage: RightModules(QQ).super_categories()
            [Category of commutative additive groups]
        """
        return [CommutativeAdditiveGroups()]

    class ParentMethods:
        pass

    class ElementMethods:
        ## x * r
        pass