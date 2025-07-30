# sage_setup: distribution = sagemath-categories
"""
CPU Detection
"""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

import os


def ncpus():
    """
    Return the number of available CPUs in the system.

    ALGORITHM: :func:`os.sched_getaffinity` or :func:`os.cpu_count`

    EXAMPLES::

        sage: sage.parallel.ncpus.ncpus()  # random output -- depends on machine
        2
    """
    # Support Sage environment variable SAGE_NUM_THREADS
    # NOTE: while doctesting, this is forced to be 2 by the
    # sage-runtests script
    try:
        n = os.environ["SAGE_NUM_THREADS"]
    except KeyError:
        pass
    else:
        return int(n)

    n = None

    if hasattr(os, 'sched_getaffinity'):
        n = len(os.sched_getaffinity(0))

    return n or os.cpu_count() or 1