# sage_setup: distribution = sagemath-categories
"""
Examples of graphs
"""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

# ****************************************************************************
#  Copyright (C) 2015 Travis Scrimshaw <tscrim at ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  https://www.gnu.org/licenses/
# *****************************************************************************
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element_wrapper import ElementWrapper
from sage.categories.graphs import Graphs


class Cycle(UniqueRepresentation, Parent):
    r"""
    An example of a graph: the cycle of length `n`.

    This class illustrates a minimal implementation of a graph.

    EXAMPLES::

        sage: from sage.categories.graphs import Graphs
        sage: C = Graphs().example(); C
        An example of a graph: the 5-cycle

        sage: C.category()
        Category of graphs

    We conclude by running systematic tests on this graph::

        sage: TestSuite(C).run()
    """
    def __init__(self, n=5):
        r"""
        EXAMPLES::

            sage: from sage.categories.graphs import Graphs
            sage: C = Graphs().example(6); C
            An example of a graph: the 6-cycle

        TESTS::

            sage: TestSuite(C).run()
        """
        self._n = n
        Parent.__init__(self, category=Graphs())

    def _repr_(self):
        r"""
        TESTS::

            sage: from sage.categories.graphs import Graphs
            sage: Graphs().example()
            An example of a graph: the 5-cycle
        """
        return "An example of a graph: the {}-cycle".format(self._n)

    def an_element(self):
        r"""
        Return an element of the graph, as per
        :meth:`Sets.ParentMethods.an_element`.

        EXAMPLES::

            sage: from sage.categories.graphs import Graphs
            sage: C = Graphs().example()
            sage: C.an_element()
            0
        """
        return self(0)

    def vertices(self):
        """
        Return the vertices of ``self``.

        EXAMPLES::

            sage: from sage.categories.graphs import Graphs
            sage: C = Graphs().example()
            sage: C.vertices()
            [0, 1, 2, 3, 4]
        """
        return [self(i) for i in range(self._n)]

    def edges(self):
        """
        Return the edges of ``self``.

        EXAMPLES::

            sage: from sage.categories.graphs import Graphs
            sage: C = Graphs().example()
            sage: C.edges()
            [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
        """
        return [self( (i, (i+1) % self._n) ) for i in range(self._n)]

    class Element(ElementWrapper):
        def dimension(self):
            """
            Return the dimension of ``self``.

            EXAMPLES::

                sage: from sage.categories.graphs import Graphs
                sage: C = Graphs().example()
                sage: e = C.edges()[0]
                sage: e.dimension()
                2
                sage: v = C.vertices()[0]
                sage: v.dimension()
                1
            """
            if isinstance(self.value, tuple):
                return 2
            return 1


Example = Cycle