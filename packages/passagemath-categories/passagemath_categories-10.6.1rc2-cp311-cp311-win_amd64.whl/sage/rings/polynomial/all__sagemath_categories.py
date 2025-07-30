# sage_setup: distribution = sagemath-categories
# Quotient of polynomial ring


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from sage.rings.polynomial.polynomial_quotient_ring import PolynomialQuotientRing
from sage.rings.polynomial.polynomial_quotient_ring_element import PolynomialQuotientRingElement

# Univariate Polynomial Rings
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.polynomial.polynomial_ring import polygen, polygens
from sage.rings.polynomial.polynomial_element import Polynomial

# Multivariate Polynomial Rings
from sage.rings.polynomial.term_order import TermOrder
from sage.rings.polynomial.multi_polynomial_element import degree_lowest_rational_function

# Infinite Polynomial Rings
from sage.rings.polynomial.infinite_polynomial_ring import InfinitePolynomialRing

# Laurent Polynomial Rings
from sage.rings.polynomial.laurent_polynomial_ring import LaurentPolynomialRing

# Evaluation of cyclotomic polynomials
from sage.rings.polynomial.cyclotomic import cyclotomic_value
