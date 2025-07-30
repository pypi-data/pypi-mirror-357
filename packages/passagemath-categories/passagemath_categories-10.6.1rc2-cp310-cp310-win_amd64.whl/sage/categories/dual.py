# sage_setup: distribution = sagemath-categories
"""
Dual functorial construction

AUTHORS:

 - Nicolas M. Thiery (2009-2010): initial revision
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
#  Copyright (C) 2009 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

# could do SelfDualCategory

from sage.categories.covariant_functorial_construction import CovariantFunctorialConstruction, CovariantConstructionCategory


class DualFunctor(CovariantFunctorialConstruction):
    """
    A singleton class for the dual functor
    """
    _functor_name = "dual"
    _functor_category = "DualObjects"
    symbol = "^*"


class DualObjectsCategory(CovariantConstructionCategory):

    _functor_category = "DualObjects"

    def _repr_object_names(self):
        """
        EXAMPLES::

            sage: VectorSpaces(QQ).DualObjects() # indirect doctest
            Category of duals of vector spaces over Rational Field
        """
        # Just to remove the `objects`
        return "duals of %s" % (self.base_category()._repr_object_names())