"""Storage backends for TaskDaily."""

from .factory import StorageFactory
from .file_storage import FileStorage

__all__ = ["StorageFactory", "FileStorage"]

# Set default storage type
default_storage = "file"
