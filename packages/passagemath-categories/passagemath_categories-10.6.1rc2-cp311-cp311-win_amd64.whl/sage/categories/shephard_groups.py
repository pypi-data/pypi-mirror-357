# sage_setup: distribution = sagemath-categories
r"""
Shephard Groups
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
#  Copyright (C) 2016 Travis Scrimshaw <tscrim at ucdavis.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.categories.category_singleton import Category_singleton
from sage.categories.generalized_coxeter_groups import GeneralizedCoxeterGroups
from sage.misc.cachefunc import cached_method


class ShephardGroups(Category_singleton):
    r"""
    The category of Shephard groups.

    EXAMPLES::

        sage: from sage.categories.shephard_groups import ShephardGroups
        sage: C = ShephardGroups(); C
        Category of shephard groups

    TESTS::

        sage: TestSuite(C).run()
    """
    @cached_method
    def super_categories(self):
        """
        EXAMPLES::

            sage: from sage.categories.shephard_groups import ShephardGroups
            sage: ShephardGroups().super_categories()
            [Category of finite generalized Coxeter groups]
        """
        return [GeneralizedCoxeterGroups().Finite()]