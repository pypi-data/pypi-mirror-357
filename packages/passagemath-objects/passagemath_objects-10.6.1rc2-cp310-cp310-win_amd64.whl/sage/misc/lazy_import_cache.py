# sage_setup: distribution = sagemath-objects
"""
Lazy import cache
"""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_objects.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

import os
import hashlib

from sage.env import SAGE_LIB, DOT_SAGE


def get_cache_file():
    """
    Return the canonical filename for caching names of lazily imported
    modules.

    EXAMPLES::

        sage: from sage.misc.lazy_import_cache import get_cache_file
        sage: get_cache_file()
        '...-lazy_import_cache.pickle'
        sage: get_cache_file().startswith(DOT_SAGE)
        True
        sage: 'cache' in get_cache_file()
        True

    It should not matter whether DOT_SAGE ends with a slash::

        sage: OLD = DOT_SAGE
        sage: sage.misc.lazy_import_cache.DOT_SAGE = '/tmp'
        sage: get_cache_file().startswith('/tmp/')
        True
        sage: sage.misc.lazy_import_cache.DOT_SAGE = OLD
    """
    mangled = hashlib.sha256(os.path.realpath(SAGE_LIB).encode('utf-8')).hexdigest()
    return os.path.join(DOT_SAGE, 'cache',
                        "%s-lazy_import_cache.pickle" % mangled)