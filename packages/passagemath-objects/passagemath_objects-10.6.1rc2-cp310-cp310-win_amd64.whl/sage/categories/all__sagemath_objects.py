# sage_setup: distribution = sagemath-objects
# Subset of sage.categories.all that is made available by the sage-objects distribution


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_objects.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from sage.misc.lazy_import import lazy_import

# Resolve a circular import so that "import sage.categories.all" can succeed
# in initializing the category system.
import sage.structure.category_object  # imports sage.categories.category

# Small part of "from sage.categories.basic import *":
from sage.categories.objects import Objects
from sage.categories.sets_cat import Sets, EmptySetError


from sage.categories.category import Category

from sage.categories.category_types import Elements

from sage.categories.cartesian_product import cartesian_product

from sage.categories.functor import (ForgetfulFunctor,
                                     IdentityFunctor)

from sage.categories.homset import (Hom, hom,
                                    End, end,
                                    Homset, HomsetWithBase)

from sage.categories.morphism import Morphism

from sage.categories.realizations import Realizations

from sage.categories.sets_with_partial_maps import SetsWithPartialMaps
del lazy_import
