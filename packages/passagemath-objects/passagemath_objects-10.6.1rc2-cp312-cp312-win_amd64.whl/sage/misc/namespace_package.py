# sage_setup: distribution = sagemath-objects
"""
Utility functions for namespace packages in Sage
"""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'passagemath_objects.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from importlib import import_module


def install_doc(package, doc):
    """
    Install the docstring ``doc`` to the package.

    TESTS:

        sage: from sage.misc.namespace_package import install_doc
        sage: install_doc('sage', 'hello')
        sage: from inspect import getdoc
        sage: getdoc(sage)
        'hello'
    """
    pkg = import_module(package)
    pkg.__doc__ = doc         # enable sage.package?
    pkg.getdoc = lambda: doc  # enable help(sage.package)


def install_dict(package, dic):
    """
    Install ``dic`` to the ``__dict__`` of the package.

    TESTS:

        sage: from sage.misc.namespace_package import install_dict
        sage: install_dict('sage', {'greeting': 'hello'})
        sage: sage.greeting
        'hello'
    """
    pkg = import_module(package)
    pkg.__dict__.update(dic)