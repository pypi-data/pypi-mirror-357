# src/vfscript/__init__.py
from .core import (
    VFS,
    VFSException,
    VFSFileNotFoundError,
    VFSFileExistsError,
    VFSInvalidPathError,
    VFSPermissionError,
)

__all__ = [
    "VFS",
    "VFSException",
    "VFSFileNotFoundError",
    "VFSFileExistsError",
    "VFSInvalidPathError",
    "VFSPermissionError",
]
