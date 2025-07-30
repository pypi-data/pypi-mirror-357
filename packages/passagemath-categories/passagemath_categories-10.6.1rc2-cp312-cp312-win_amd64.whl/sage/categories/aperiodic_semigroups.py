# sage_setup: distribution = sagemath-categories
r"""
Aperiodic semigroups
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
#  Copyright (C) 2016 Nicolas M. Thiéry <nthiery at users.sf.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.categories.semigroups import Semigroups


class AperiodicSemigroups(CategoryWithAxiom):
    def extra_super_categories(self):
        r"""
        Implement the fact that an aperiodic semigroup is `H`-trivial.

        EXAMPLES::

            sage: Semigroups().Aperiodic().extra_super_categories()
            [Category of h trivial semigroups]
        """
        return [Semigroups().HTrivial()]