# sage_setup: distribution = sagemath-categories
# sage.doctest: needs sage.groups
r"""
Groupoid
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
#  Copyright (C) 2008 David Kohel <kohel@maths.usyd.edu> and
#                     William Stein <wstein@math.ucsd.edu>
#                     Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.categories.category import CategoryWithParameters
from sage.categories.sets_cat import Sets


class Groupoid(CategoryWithParameters):
    """
    The category of groupoids, for a set (usually a group) `G`.

    FIXME:

     - Groupoid or Groupoids ?
     - definition and link with :wikipedia:`Groupoid`
     - Should Groupoid inherit from Category_over_base?

    EXAMPLES::

        sage: Groupoid(DihedralGroup(3))
        Groupoid with underlying set Dihedral group of order 6 as a permutation group
    """

    def __init__(self, G=None):
        """
        TESTS::

            sage: S8 = SymmetricGroup(8)
            sage: C = Groupoid(S8)
            sage: TestSuite(C).run()
        """
        CategoryWithParameters.__init__(self)  # "Groupoid")
        if G is None:
            from sage.groups.perm_gps.permgroup_named import SymmetricGroup
            G = SymmetricGroup(8)
        self.__G = G

    def _repr_(self):
        """
        EXAMPLES::

            sage: S8 = SymmetricGroup(8)
            sage: Groupoid(S8)
            Groupoid with underlying set Symmetric group of order 8! as a permutation group
        """
        return "Groupoid with underlying set %s" % self.__G

    # def construction(self):
    #     return (self.__class__, self.__G)

    def _make_named_class_key(self, name):
        """
        The parent/element classes of all groupoids coincide.

        EXAMPLES::

            sage: Groupoid(DihedralGroup(3)).parent_class is Groupoid(ZZ).parent_class
            True
        """
        return None

    def super_categories(self):
        """
        EXAMPLES::

            sage: Groupoid(DihedralGroup(3)).super_categories()
            [Category of sets]
        """
        return [Sets()] # ???

    @classmethod
    def an_instance(cls):
        """
        Return an instance of this class.

        EXAMPLES::

            sage: Groupoid.an_instance() # indirect doctest
            Groupoid with underlying set Symmetric group of order 8! as a permutation group
        """
        from sage.groups.perm_gps.permgroup_named import SymmetricGroup
        G = SymmetricGroup(8)
        return cls(G)