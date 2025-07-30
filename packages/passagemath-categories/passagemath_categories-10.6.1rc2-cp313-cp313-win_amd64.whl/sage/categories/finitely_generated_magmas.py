# sage_setup: distribution = sagemath-categories
r"""
Finitely generated magmas
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
#  Copyright (C) 2014 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.abstract_method import abstract_method
from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.categories.magmas import Magmas


class FinitelyGeneratedMagmas(CategoryWithAxiom):
    r"""
    The category of finitely generated (multiplicative) magmas.

    See :meth:`Magmas.SubcategoryMethods.FinitelyGeneratedAsMagma` for
    details.

    EXAMPLES::

        sage: C = Magmas().FinitelyGeneratedAsMagma(); C
        Category of finitely generated magmas
        sage: C.super_categories()
        [Category of magmas]
        sage: sorted(C.axioms())
        ['FinitelyGeneratedAsMagma']

    TESTS::

        sage: TestSuite(C).run()
    """

    _base_category_class_and_axiom = (Magmas, "FinitelyGeneratedAsMagma")

    class ParentMethods:

        @abstract_method
        def magma_generators(self):
            """
            Return distinguished magma generators for ``self``.

            OUTPUT: a finite family

            This method should be implemented by all
            :class:`finitely generated magmas <FinitelyGeneratedMagmas>`.

            EXAMPLES::

                sage: S = FiniteSemigroups().example()
                sage: S.magma_generators()
                Family ('a', 'b', 'c', 'd')
            """