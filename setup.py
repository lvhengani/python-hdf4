#!/usr/bin/env python
"""Python-HDF4: Python interface to the NCSA HDF4 library.

The Python-HDF4 package wraps the functionality of the NCSA HDF version
4 library inside a Python OOP framework. The SD (scientific dataset),
VS (Vdata) and V (Vgroup) APIs are currently implemented.  SD datasets
are read/written through numpy arrays. NetCDF files can also be read
and modified with Python-HDF4.

This package is a fork of pyhdf (http://pysclint.sourceforge.net/pyhdf/).
"""

from __future__ import print_function

DOCLINES = __doc__.split("\n")

# Allows bdist_egg to work if you have setuptools installed.
# This import must be before the numpy.distutils import of setup.
#  Otherwise, no harm.
try:
    import setuptools
except:
    pass

from numpy.distutils.core import setup, Extension

import sys
import os
import os.path as path

CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved
Programming Language :: C
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Software Development
Topic :: Scientific/Engineering
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

def _find_args(pat, env):
    val = os.environ.get(env, [])
    if val:
        val = val.split(os.pathsep)
    try:
        k = sys.argv.index(pat)
        val.extend(sys.argv[k+1].split(os.pathsep))
        del sys.argv[k]
        del sys.argv[k]
    except ValueError:
        pass
    return val

include_dirs = _find_args('-i', 'INCLUDE_DIRS')
library_dirs = _find_args('-l', 'LIBRARY_DIRS')
szip_installed = 'SZIP' in os.environ
compress = 'NO_COMPRESS' not in os.environ
extra_link_args = os.environ.get('LINK_ARGS', '')


msg = 'Cannot proceed without the HDF4 library.  Please ' \
      'export INCLUDE_DIRS and LIBRARY_DIRS as explained' \
      'in the INSTALL file.'

if sys.platform.startswith('linux'):
    # libhdf4 header files on most linux distributations
    # (e.g. Debian/Ubuntu, CentOS) are stored in /usr/include/hdf
    d = "/usr/include/hdf/"
    if not include_dirs and os.path.exists(d):
        include_dirs.append(d)

if sys.platform == 'win32':
    try:
        k = sys.argv.index('--hdf4')
        baseloc = sys.argv[k+1]
        del sys.argv[k]
        del sys.argv[k]
    except (ValueError, IndexError):
        baseloc = None
    if not baseloc:
        baseloc = os.environ.get('HDF4', None)
    if baseloc:
        # fix include_dirs and library_dirs
        #  based on fixed set of paths
        if not path.exists(baseloc):
            print("\n******\n%s not found\n******\n\n" % baseloc)
            raise RuntimeError(msg)
        if not path.isdir(baseloc):
            print("\n******\n%s not a directory \n******\n\n" % baseloc)
            raise RuntimeError(msg)
        alldirs = os.listdir(baseloc)
        include_dirs = []
        library_dirs = []
        for adir in alldirs:
            if not path.isdir(path.sep.join([baseloc, adir])):
                continue
            if adir.startswith('42'):
                include_dirs.append(path.sep.join([baseloc, adir, 'include']))
                library_dirs.append(path.sep.join([baseloc, adir, 'dll']))
            library_dirs.append(path.sep.join([baseloc, adir, 'lib']))
        print("Using include_dirs = ", include_dirs)
        print("Using library_dirs = ", library_dirs)

for p in include_dirs + library_dirs:
    if not path.exists(p):
        print("\n******\n%s not found\n******\n\n" % p)
        raise RuntimeError(msg)

if sys.platform == 'win32':
    # Find DLL path
    dll_path = ''
    for p in library_dirs:
        if path.exists(p + os.path.sep + "HM423M.DLL"):
            dll_path = p + os.path.sep
            break
    if dll_path == '':
        raise RuntimeError("Cannot find required HDF4 DLLs -- check LIBRARY_DIRS")

if sys.platform == 'win32':
    libraries = ["hm423m", "hd423m", "xdr_for_dll" ]
else:
    libraries = ["mfhdf", "df"]

if szip_installed:
    extra_compile_args = []
    if sys.platform == 'win32':
        libraries += ["szlib"]
    else:
        libraries += ["sz"]
else:
    extra_compile_args = ["-DNOSZIP"]
if sys.platform == 'win32':
    libraries += ["libjpeg", "zlib", "ws2_32"]
else:
    libraries += ["jpeg", "z"]

if not compress:
    extra_compile_args += ["-DNOCOMPRESS"]

_hdfext = Extension('pyhdf._hdfext',
                    sources      = ["pyhdf/hdfext_wrap.c"],
                    include_dirs = include_dirs,
                    extra_compile_args = extra_compile_args,
                    library_dirs = library_dirs,
                    extra_link_args=[extra_link_args],
                    libraries = libraries,
                    )

if sys.platform == 'win32':
    data_files = [("pyhdf", [dll_path + x for x in ["HM423M.DLL", "HD423M.DLL"]])]
else:
    data_files = []

setup(name         = 'python-hdf4',
      maintainer       = 'python-hdf4 authors',
      maintainer_email = 'fshahriar@gmail.com',
      author       = 'Andre Gosselin et al.',
      description  = DOCLINES[0],
      keywords     = ['hdf4', 'netcdf', 'numpy', 'python', 'pyhdf'],
      license      = 'MIT',
      long_description = "\n".join(DOCLINES[2:]),
      url          = 'https://github.com/fhs/python-hdf4',
      version      = '0.9.1',
      packages     = ['pyhdf'],
      ext_modules  = [_hdfext],
      data_files   = data_files,
      provides     = ['pyhdf'],
      classifiers  = [_f for _f in CLASSIFIERS.split('\n') if _f],
      platforms    = ["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
      )
