# src/vfscript/__init__.py
from .core import *

__all__ = [
    "VFS",
    "VFSException",
    "VFSFileNotFoundError",
    "VFSFileExistsError",
    "VFSInvalidPathError",
    "VFSPermissionError",
]

