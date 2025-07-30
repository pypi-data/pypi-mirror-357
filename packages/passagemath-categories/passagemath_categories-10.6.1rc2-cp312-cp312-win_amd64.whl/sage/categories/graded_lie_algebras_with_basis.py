# sage_setup: distribution = sagemath-categories
r"""
Graded Lie Algebras With Basis
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
#       Copyright (C) 2018 Travis Scrimshaw <tcscrims at gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

from sage.categories.graded_modules import GradedModulesCategory
from sage.misc.lazy_import import LazyImport


class GradedLieAlgebrasWithBasis(GradedModulesCategory):
    """
    The category of graded Lie algebras with a distinguished basis.

    EXAMPLES::

        sage: C = LieAlgebras(ZZ).WithBasis().Graded(); C
        Category of graded Lie algebras with basis over Integer Ring
        sage: C.super_categories()
        [Category of graded modules with basis over Integer Ring,
         Category of Lie algebras with basis over Integer Ring,
         Category of graded Lie algebras over Integer Ring]

        sage: C is LieAlgebras(ZZ).WithBasis().Graded()
        True
        sage: C is LieAlgebras(ZZ).Graded().WithBasis()
        False

    TESTS::

        sage: TestSuite(C).run()
    """
    FiniteDimensional = LazyImport('sage.categories.finite_dimensional_graded_lie_algebras_with_basis',
                                  'FiniteDimensionalGradedLieAlgebrasWithBasis',
                                  as_name='FiniteDimensional')