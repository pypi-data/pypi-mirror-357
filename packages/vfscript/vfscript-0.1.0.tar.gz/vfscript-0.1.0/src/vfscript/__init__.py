# src/vfsdoc/__init__.py
from vfscript import (
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
