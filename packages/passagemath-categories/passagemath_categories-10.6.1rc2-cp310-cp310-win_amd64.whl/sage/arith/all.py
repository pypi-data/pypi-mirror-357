# sage_setup: distribution = sagemath-categories


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from sage.arith.all__sagemath_objects import *

from sage.misc.lazy_import import lazy_import

from sage.arith.misc import (algdep, algebraic_dependency,
                             bernoulli, is_prime, is_prime_power,
                             is_pseudoprime, is_pseudoprime_power,
                             prime_powers, primes_first_n, eratosthenes, primes,
                             next_prime_power, next_probable_prime, next_prime,
                             previous_prime, previous_prime_power, random_prime,
                             divisors, sigma, gcd, GCD, xlcm, xgcd, xkcd,
                             inverse_mod, get_gcd, get_inverse_mod, power_mod,
                             rational_reconstruction, mqrr_rational_reconstruction,
                             trial_division, factor, prime_divisors, odd_part, prime_to_m_part,
                             is_square, is_squarefree, euler_phi, carmichael_lambda, crt, CRT,
                             CRT_list, CRT_basis, CRT_vectors, multinomial, multinomial_coefficients,
                             binomial, factorial, kronecker_symbol, kronecker, legendre_symbol,
                             primitive_root, nth_prime, quadratic_residues, moebius,
                             continuant, number_of_divisors, hilbert_symbol, hilbert_conductor,
                             hilbert_conductor_inverse, falling_factorial, rising_factorial,
                             integer_ceil, integer_floor,
                             two_squares, three_squares, four_squares, sum_of_k_squares,
                             subfactorial, is_power_of_two, differences,
                             sort_complex_numbers_for_display,
                             fundamental_discriminant, squarefree_divisors,
                             radical, binomial_coefficients, jacobi_symbol,
                             dedekind_sum,
                             prime_factors, prime_range, valuation)

from sage.arith.functions import lcm
LCM = lcm

from sage.arith.srange import xsrange, srange, ellipsis_iter, ellipsis_range
sxrange = xsrange

σ = sigma
del lazy_import
