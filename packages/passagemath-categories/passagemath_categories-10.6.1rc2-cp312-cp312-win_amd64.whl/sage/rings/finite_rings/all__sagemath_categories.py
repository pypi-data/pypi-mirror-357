# sage_setup: distribution = sagemath-categories


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from sage.rings.finite_rings.finite_field_constructor import FiniteField

GF = FiniteField

from sage.rings.finite_rings.conway_polynomials import conway_polynomial, exists_conway_polynomial

# Finite residue fields
from sage.rings.finite_rings.residue_field import ResidueField
