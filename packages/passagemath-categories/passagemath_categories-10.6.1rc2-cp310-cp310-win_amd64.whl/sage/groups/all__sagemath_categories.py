# sage_setup: distribution = sagemath-categories


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from sage.groups.all__sagemath_objects import *

from sage.groups.generic import (discrete_log, discrete_log_rho, discrete_log_lambda,
                                 linear_relation, multiple, multiples, order_from_multiple)

from sage.misc.lazy_import import lazy_import

lazy_import('sage.groups', 'groups_catalog', 'groups')

del lazy_import
