# Licensed under the MIT License.
# pytypex Copyright (C) 2022 numlinka.

"""
Standard Type Extensions

Provides some type extensions that the standard library does not meet.
"""

__all__ = [
    "Static",
    "Abstract",
    "Singleton",
    "Multiton",
    "Atomic",
    "AbsoluteAtomic",
    "MultitonAtomic",
    "abstractmethod",

    "FilePath",
    "DirectoryPath",
    "FinalFilePath",
    "FinalDirectoryPath",
    "Directory",

    "mutex",
    "once"
]

__name__ = "typex"
__author__ = "numlinka"
__license__ = "MIT"
__copyright__ = "Copyright (C) 2022 numlinka"

__version_info__ = (0, 3, 3)
__version__ = ".".join(map(str, __version_info__))

# internal
from . import constants
from .basic import Static, Abstract, Singleton, Multiton, Atomic, AbsoluteAtomic, MultitonAtomic, abstractmethod
from .dirstruct import FilePath, DirectoryPath, FinalFilePath, FinalDirectoryPath, Directory
from .decorators import mutex, once
