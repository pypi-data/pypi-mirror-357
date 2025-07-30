# sage_setup: distribution = sagemath-categories
r"""
Graded bialgebras
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
#                2011 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************


def GradedBialgebras(base_ring):
    """
    The category of graded bialgebras.

    EXAMPLES::

        sage: C = GradedBialgebras(QQ); C
        Join of Category of graded algebras over Rational Field
            and Category of bialgebras over Rational Field
            and Category of graded coalgebras over Rational Field
        sage: C is Bialgebras(QQ).Graded()
        True

    TESTS::

        sage: TestSuite(C).run()
    """
    from sage.categories.bialgebras import Bialgebras
    return Bialgebras(base_ring).Graded()