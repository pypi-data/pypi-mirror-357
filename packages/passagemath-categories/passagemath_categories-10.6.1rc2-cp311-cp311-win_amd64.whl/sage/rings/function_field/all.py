# sage_setup: distribution = sagemath-categories


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from sage.rings.function_field.all__sagemath_modules import *

try:
    from sage.rings.function_field.all__sagemath_symbolics import *
except ImportError:
    pass
