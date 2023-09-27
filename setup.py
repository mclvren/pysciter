#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from shutil import rmtree
from sys import maxsize
from platform import system, machine
from enum import StrEnum
from urllib.request import urlretrieve
from pathlib import Path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


    class bdist_wheel(_bdist_wheel):

        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            # Mark us as not a pure python package
            self.root_is_pure = False

        def get_tag(self):
            python, abi, plat = _bdist_wheel.get_tag(self)
            python, abi = 'py3', 'none'
            return python, abi, plat
except ImportError:
    bdist_wheel = None

LIB_PATH = Path.cwd().joinpath('sciter').joinpath('capi').joinpath('lib')


class StringEnum(StrEnum):
    @classmethod
    def values(cls):
        """Returns a list of all the enum values."""
        return list(cls._value2member_map_.keys())


class System(StringEnum):
    """Supported platforms"""
    linux = 'Linux'
    darwin = 'Darwin'
    windows = 'Windows'


class Machine(StringEnum):
    """Supported architectures"""
    x32 = 'x86'
    x64 = 'x86_64'
    arm32 = 'arm32'
    arm64 = 'arm64'


SYSTEM = system()
_MACHINE = machine()

# Simplify arm architectures
if 'arm' not in _MACHINE:
    MACHINE = _MACHINE
else:
    if maxsize > 2 ** 32:
        MACHINE = 'arm64'
    else:
        MACHINE = 'arm32'

# Check supported
if SYSTEM not in System.values():
    raise Exception(f"System {SYSTEM} not supported!")

if MACHINE not in Machine.values():
    raise Exception(f"Architecture {MACHINE} not supported!")


def clean_lib_folder():
    """Cleans platform libraries"""
    for path in Path(LIB_PATH).glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            rmtree(path)


def retrieve_lib():
    """
    Downloads latest platform libraries
    from https://gitlab.com/sciter-engine/sciter-js-sdk/-/tree/main/bin?ref_type=heads
    """
    url = 'https://gitlab.com/sciter-engine/sciter-js-sdk/-/raw/main/bin/'
    system_type = System(SYSTEM)
    machine_type = Machine(MACHINE)

    if system_type == System.linux:
        url += 'linux/'
        if machine_type in (Machine.x32, Machine.x64):
            url += 'x64/libsciter.so'
        if machine_type == Machine.arm32:
            url += 'arm32/libsciter-gtk.so'
        if machine_type == Machine.arm64:
            url += 'arm64/libsciter.so'

    if system_type == System.darwin:
        url += 'macosx/libsciter.dylib'

    if system_type == System.windows:
        url += 'windows/'
        if machine_type == Machine.x32:
            url += 'x32/'
        if machine_type == Machine.x64:
            url += 'x64/'
        if machine_type == Machine.arm64:
            url += 'arm64/'
        url += 'sciter.dll'

    filename = LIB_PATH.joinpath(url.rsplit('/', 1)[-1])
    clean_lib_folder()
    urlretrieve(url, filename)


config = {
    'name': 'PySciter',
    'author': 'pravic',
    'author_email': 'ehysta@gmail.com',
    'description': 'Python bindings for the Sciter - Embeddable HTML/CSS/script engine (cross-platform desktop GUI toolkit).',
    'url': 'https://github.com/sciter-sdk/pysciter/',
    'download_url': 'https://github.com/sciter-sdk/pysciter/releases',
    'bugtrack_url': 'https://github.com/sciter-sdk/pysciter/issues',
    'version': '0.6.9',
    'platforms': ['Windows', 'Linux', 'MacOS X', ],
    'packages': ['sciter', 'sciter.capi'],
    'package_data': {'sciter.capi': ['lib/*']},
    'install_requires': [''],
    'scripts': [],
    'keywords': ['gui', 'sciter', 'javascript', 'tiscript', 'htmlayout', 'html', 'css', 'web', 'cross-platform', ],
    'license': 'MIT',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows :: Windows XP',
        'Operating System :: Microsoft :: Windows :: Windows Vista',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: GTK',
        'Environment :: Web Environment',
        'Programming Language :: C++',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Desktop Environment',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Widget Sets',
    ],
    'cmdclass': {'bdist_wheel': bdist_wheel},
    'long_description': """
Introduction
============
Sciter (https://sciter.com) is an embeddable HTML/CSS/script engine with GPU accelerated rendering for desktop application UI.
It's a compact, single dll/dylib/so file (4-8 mb), engine without any additional dependencies.

Sciter uses Direct2D GPU accelerated graphics on modern Windows versions and GDI+ on XP.
On OS X, it uses standard CoreGraphics primitives, while the Linux version uses Cairo.

Sciter uses HTML5 set of elements, implements CSS level 2.1 in full, plus the most popular features of CSS level 3.
It also contains custom CSS extensions that are required to support desktop UI cases.
For example, flex units and various layout managers.

Check the `screenshot gallery <https://github.com/oskca/sciter#sciter-desktop-ui-examples>`_ of the desktop UI examples.


Installation
============

For installation instructions and usage examples please refer to `github project page <https://github.com/sciter-sdk/pysciter#getting-started>`_.


Compatibility
=============

PySciter requires Python 3.x.

Sciter works on:

- Microsoft Windows XP and above (x86/x64)
- macOS v 10.7 and above (64-bit)
- Linux/GTK (GTK v 3.0 and above, 64-bit only)
- Raspberry Pi


Feedback and getting involved
=============================
- PySciter Code Repository: https://github.com/sciter-sdk/pysciter
- Issue tracker: https://github.com/sciter-sdk/pysciter/issues
- Sciter official website: https://sciter.com
- Sciter forum: https://sciter.com/forums/
- Sciter SDK: https://github.com/c-smile/sciter-sdk

""",
}

retrieve_lib()
setup(**config)
