from typing import Dict, Type

from ..core.interfaces.storage import StorageInterface
from .file_storage import FileStorage


class StorageFactory:
    """Factory for creating storage backends."""

    _storage_types: Dict[str, Type[StorageInterface]] = {
        "file": FileStorage,
    }

    @classmethod
    def create_storage(cls, storage_type: str = "file", **kwargs) -> StorageInterface:
        """Create a storage backend instance.

        Args:
            storage_type: Type of storage to create (currently only 'file' is supported)
            **kwargs: Additional arguments for storage initialization

        Returns:
            Storage backend instance

        Raises:
            ValueError: If storage type is not supported
        """
        if storage_type != "file":
            raise ValueError("Only 'file' storage type is supported")

        return FileStorage(**kwargs)

    @classmethod
    def register_storage(cls, name: str, storage_class: Type[StorageInterface]) -> None:
        """Register a new storage type."""
        if not issubclass(storage_class, StorageInterface):
            raise StorageError(
                f"Storage class must inherit from StorageInterface: {storage_class}"
            )
        cls._storage_types[name.lower()] = storage_class

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported storage types."""
        return list(cls._storage_types.keys())
