# sage_setup: distribution = sagemath-objects
"""
Subquotient Functorial Construction

AUTHORS:

 - Nicolas M. Thiery (2010): initial revision
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
#  Copyright (C) 2009 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.categories.covariant_functorial_construction import RegressiveCovariantConstructionCategory


class SubquotientsCategory(RegressiveCovariantConstructionCategory):

    _functor_category = "Subquotients"