# sage_setup: distribution = sagemath-objects
r"""
SetsWithPartialMaps
"""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_objects.libs'))):
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

from sage.categories.category_singleton import Category_singleton
from sage.categories.objects import Objects


class SetsWithPartialMaps(Category_singleton):
    """
    The category whose objects are sets and whose morphisms are
    maps that are allowed to raise a :exc:`ValueError` on some inputs.

    This category is equivalent to the category of pointed sets,
    via the equivalence sending an object X to X union {error},
    a morphism f to the morphism of pointed sets that sends x
    to f(x) if f does not raise an error on x, or to error if it
    does.

    EXAMPLES::

        sage: SetsWithPartialMaps()
        Category of sets with partial maps

        sage: SetsWithPartialMaps().super_categories()
        [Category of objects]

    TESTS::

        sage: TestSuite(SetsWithPartialMaps()).run()
    """
    #def __call__(self, X, pt):
    #    import sage.sets.all
    #    return sage.sets.all.Set(X, pt)

    def super_categories(self):
        """
        EXAMPLES::

            sage: SetsWithPartialMaps().super_categories()
            [Category of objects]
        """
        return [Objects()]