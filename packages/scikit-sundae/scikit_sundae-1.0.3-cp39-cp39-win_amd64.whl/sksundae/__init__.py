"""
scikit-SUNDAE provides Python bindings to `SUNDIALS`_ integrators. The implicit
differential algebraic (IDA) solver and C-based variable-coefficient ordinary
differential equations (CVODE) solver are both included.

The name SUNDAE combines (SUN)DIALS and DAE, which stands for differential
algebraic equations. Solvers specific to DAE problems are not frequently
available in Python. An ordinary differential equation (ODE) solver is also
included for completeness. ODEs can be categorized as a subset of DAEs (i.e.,
DAEs with no algebraic constraints).

.. _SUNDIALS: https://sundials.readthedocs.io

Accessing the documentation
---------------------------
Documentation is accessible via Python's ``help()`` function which prints
docstrings from a package, module, function, class, etc. You can also access
the documentation by visiting the website, hosted through GitHub pages. The
website includes search functionality and more detailed examples.

Acknowledgements
----------------
scikit-SUNDAE was written by researchers at the **National Renewable Energy
Laboratory (NREL)**, primarily to solve physics-based battery models. Modeling
in Python typically allows for rapid development and makes code more shareable.
However, there was an identified gap in Python's numerical computing ecosystem:
the lack of accessible DAE solvers. While ODE solvers are widely available in
many packages, DAE solvers are not as prevalent.

scikit-SUNDAE started out as a lighter-weight and easy-to-install alternative
to `scikits.odes`_, which similarly provides SUNDIALS bindings, but requires
building from source. The goal was to offer a simpler installation process,
with binary distributions that are consistent across major platforms (PyPI and
conda). While scikit-SUNDAE's API was mostly modeled after scikits.odes, we
want to point out that our codebase was written from scratch and that this is
a separate, independent package. During development we prioritized:

1. Using scipy-like output containers
2. Adopting event function APIs like `scipy.integrate`_, with a few exceptions
3. Maintaining and testing builds using SUNDIALS releases on `conda-forge`_
4. Setuping the package for binary distribution

Since scikit-SUNDAE installations may include pre-built SUNDIALS libraries, the
`SUNDIALS license`_ is linked here and is also included with all distributions.
SUNDIALS also requires that their copyright be shared: Copyright (c) 2002-2024,
Lawrence Livermore National Security and Southern Methodist University. All
rights reserved.

.. _scikits.odes: https://scikits-odes.readthedocs.io
.. _conda-forge: https://anaconda.org/conda-forge/sundials
.. _scipy.integrate: https://docs.scipy.org/doc/scipy/reference/integrate.html
.. _SUNDIALS license: https://github.com/LLNL/sundials/blob/main/LICENSE

"""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'scikit_sundae.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-scikit_sundae-1.0.3')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-scikit_sundae-1.0.3')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from ._cy_common import SUNDIALS_VERSION

from . import ida
from . import utils
from . import cvode

__all__ = ['ida', 'utils', 'cvode', 'SUNDIALS_VERSION']

__version__ = '1.0.3'