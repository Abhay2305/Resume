import os
import shutil
from abc import ABC, abstractmethod

class StorageProvider(ABC):
    @abstractmethod
    def upload_file(self, file_name: str, file_content: bytes) -> str:
        """Uploads a file and returns the accessible URL or path."""
        pass

    @abstractmethod
    def get_file(self, file_name: str) -> bytes:
        """Retrieves file binary content."""
        pass

    @abstractmethod
    def delete_file(self, file_name: str) -> bool:
        """Deletes file from storage."""
        pass

class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # Save files inside backend/storage
            base_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "storage"
            )
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def upload_file(self, file_name: str, file_content: bytes) -> str:
        file_path = os.path.join(self.base_dir, file_name)
        # Ensure subdirectories exist if file_name is a relative path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_content)
        # Return local absolute path (could be mapped to a static serve URL in FastAPI)
        return file_path

    def get_file(self, file_name: str) -> bytes:
        file_path = os.path.join(self.base_dir, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_name} not found in local storage.")
        with open(file_path, "rb") as f:
            return f.read()

    def delete_file(self, file_name: str) -> bool:
        file_path = os.path.join(self.base_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

# Export the active provider instance
def get_storage_provider() -> StorageProvider:
    # Easy switch point: return CloudflareR2StorageProvider() or S3StorageProvider()
    return LocalStorageProvider()
