# sage_setup: distribution = sagemath-categories
r"""
Abstract base classes for interface elements
"""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

class AxiomElement:
    r"""
    Abstract base class for :class:`~sage.interfaces.axiom.AxiomElement`.

    This class is defined for the purpose of ``isinstance`` tests.  It should not be
    instantiated.

    EXAMPLES:

    By design, there is a unique direct subclass::

        sage: len(sage.interfaces.abc.AxiomElement.__subclasses__()) <= 1
        True
    """
    pass


class ExpectElement:
    r"""
    Abstract base class for :class:`~sage.interfaces.expect.ExpectElement`.

    This class is defined for the purpose of ``isinstance`` tests.  It should not be
    instantiated.

    EXAMPLES:

    By design, there is a unique direct subclass::

        sage: len(sage.interfaces.abc.ExpectElement.__subclasses__()) <= 1
        True
    """
    pass


class FriCASElement:
    r"""
    Abstract base class for :class:`~sage.interfaces.fricas.FriCASElement`.

    This class is defined for the purpose of ``isinstance`` tests.  It should not be
    instantiated.

    EXAMPLES:

    By design, there is a unique direct subclass::

        sage: len(sage.interfaces.abc.FriCASElement.__subclasses__()) <= 1
        True
    """
    pass


class GapElement:
    r"""
    Abstract base class for :class:`~sage.interfaces.gap.GapElement`.

    This class is defined for the purpose of ``isinstance`` tests.  It should not be
    instantiated.

    EXAMPLES:

    By design, there is a unique direct subclass::

        sage: len(sage.interfaces.abc.GapElement.__subclasses__()) <= 1
        True
    """
    pass


class GpElement:
    r"""
    Abstract base class for :class:`~sage.interfaces.gp.GpElement`.

    This class is defined for the purpose of ``isinstance`` tests.  It should not be
    instantiated.

    EXAMPLES:

    By design, there is a unique direct subclass::

        sage: len(sage.interfaces.abc.GpElement.__subclasses__()) <= 1
        True
    """
    pass


class Macaulay2Element:
    r"""
    Abstract base class for :class:`~sage.interfaces.macaulay2.Macaulay2Element`.

    This class is defined for the purpose of ``isinstance`` tests.  It should not be
    instantiated.

    EXAMPLES:

    By design, there is a unique direct subclass::

        sage: len(sage.interfaces.abc.Macaulay2Element.__subclasses__()) <= 1
        True
    """
    pass


class MagmaElement:
    r"""
    Abstract base class for :class:`~sage.interfaces.magma.MagmaElement`.

    This class is defined for the purpose of ``isinstance`` tests.  It should not be
    instantiated.

    EXAMPLES:

    By design, there is a unique direct subclass::

        sage: len(sage.interfaces.abc.MagmaElement.__subclasses__()) <= 1
        True
    """
    pass


class SingularElement:
    r"""
    Abstract base class for :class:`~sage.interfaces.singular.SingularElement`.

    This class is defined for the purpose of ``isinstance`` tests.  It should not be
    instantiated.

    EXAMPLES:

    By design, there is a unique direct subclass::

        sage: len(sage.interfaces.abc.SingularElement.__subclasses__()) <= 1
        True
    """
    pass