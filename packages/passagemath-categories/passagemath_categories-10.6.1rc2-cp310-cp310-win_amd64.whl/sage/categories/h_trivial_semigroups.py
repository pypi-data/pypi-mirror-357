# sage_setup: distribution = sagemath-categories
r"""
H-trivial semigroups
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


class HTrivialSemigroups(CategoryWithAxiom):
    def Finite_extra_super_categories(self):
        r"""
        Implement the fact that a finite `H`-trivial is aperiodic.

        EXAMPLES::

            sage: Semigroups().HTrivial().Finite_extra_super_categories()
            [Category of aperiodic semigroups]
            sage: Semigroups().HTrivial().Finite() is Semigroups().Aperiodic().Finite()
            True
        """
        return [Semigroups().Aperiodic()]

    def Inverse_extra_super_categories(self):
        r"""
        Implement the fact that an `H`-trivial inverse semigroup is `J`-trivial.

        .. TODO::

            Generalization for inverse semigroups.

            Recall that there are two invertibility axioms for a semigroup `S`:

            - One stating the existence, for all `x`, of a local inverse
              `y` satisfying `x=xyx` and `y=yxy`;
            - One stating the existence, for all `x`, of a global
              inverse `y` satisfying `xy=yx=1`, where `1` is the unit
              of `S` (which must of course exist).

            It is sufficient to have local inverses for `H`-triviality
            to imply `J`-triviality. However, at this stage, only the
            second axiom is implemented in Sage (see
            :meth:`Magmas.Unital.SubcategoryMethods.Inverse`). Therefore
            this fact is only implemented for semigroups with global
            inverses, that is groups. However the trivial group is the
            unique `H`-trivial group, so this is rather boring.

        EXAMPLES::

            sage: Semigroups().HTrivial().Inverse_extra_super_categories()
            [Category of j trivial semigroups]
            sage: Monoids().HTrivial().Inverse()
            Category of h trivial groups
        """
        return [self.JTrivial()]