# sage_setup: distribution = sagemath-categories
r"""
Domains
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
#                2012 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.lazy_import import LazyImport
from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.categories.rings import Rings


class Domains(CategoryWithAxiom):
    """
    The category of domains.

    A domain (or non-commutative integral domain), is a ring, not
    necessarily commutative, with no nonzero zero divisors.

    EXAMPLES::

        sage: C = Domains(); C
        Category of domains
        sage: C.super_categories()
        [Category of rings]
        sage: C is Rings().NoZeroDivisors()
        True

    TESTS::

        sage: TestSuite(C).run()
    """

    _base_category_class_and_axiom = (Rings, "NoZeroDivisors")

    def super_categories(self):
        """
        EXAMPLES::

            sage: Domains().super_categories()
            [Category of rings]
        """
        return [Rings()]

    Commutative = LazyImport('sage.categories.integral_domains', 'IntegralDomains', at_startup=True)

    class ParentMethods:
        def _test_zero_divisors(self, **options):
            """
            Check to see that there are no zero divisors.

            .. NOTE::

                In rings whose elements can not be represented exactly, there
                may be zero divisors in practice, even though these rings do
                not have them in theory. For such inexact rings, these tests
                are not performed::

                    sage: # needs sage.rings.padics
                    sage: R = ZpFM(5); R
                    5-adic Ring of fixed modulus 5^20
                    sage: R.is_exact()
                    False
                    sage: a = R(5^19)
                    sage: a.is_zero()
                    False
                    sage: (a * a).is_zero()
                    True
                    sage: R._test_zero_divisors()

            EXAMPLES::

                sage: ZZ._test_zero_divisors()
                sage: ZpFM(5)._test_zero_divisors()                                     # needs sage.rings.padics
            """
            if not self.is_exact():
                return # Can't check on inexact rings

            tester = self._tester(**options)

            # Filter out zero
            S = [s for s in tester.some_elements() if not s.is_zero()]

            from sage.misc.misc import some_tuples
            for a,b in some_tuples(S, 2, tester._max_runs):
                p = a * b
                tester.assertFalse(p.is_zero())

    class ElementMethods:
        pass