# sage_setup: distribution = sagemath-categories
"""
Reference Parallel Primitives

These are reference implementations of basic parallel
primitives. These are not actually parallel, but work the same way.
They are good for testing.
"""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from sage.misc.prandom import shuffle


def parallel_iter(f, inputs):
    """
    Reference parallel iterator implementation.

    INPUT:

    - ``f`` -- a Python function that can be pickled using
      the ``pickle_function`` command

    - ``inputs`` -- list of pickleable pairs (args, kwds), where
      args is a tuple and kwds is a dictionary

    OUTPUT: iterator over 2-tuples ``(inputs[i], f(inputs[i]))``, where the
    order may be completely random

    EXAMPLES::

        sage: def f(N, M=10): return N*M
        sage: inputs = [((2,3),{}),  (tuple(), {'M':5,'N':3}), ((2,),{})]
        sage: set_random_seed(0)
        sage: for a, val in sage.parallel.reference.parallel_iter(f, inputs):
        ....:     print((a, val))
        (((2,), {}), 20)
        (((), {'M': 5, 'N': 3}), 15)
        (((2, 3), {}), 6)
        sage: for a, val in sage.parallel.reference.parallel_iter(f, inputs):
        ....:     print((a, val))
        (((), {'M': 5, 'N': 3}), 15)
        (((2,), {}), 20)
        (((2, 3), {}), 6)
    """
    v = list(inputs)
    shuffle(v)
    for args, kwds in v:
        yield ((args, kwds), f(*args, **kwds))