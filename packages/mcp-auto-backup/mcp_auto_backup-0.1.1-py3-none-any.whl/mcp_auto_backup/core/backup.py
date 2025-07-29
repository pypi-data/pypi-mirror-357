"""
Core backup management for MCP Auto Backup.

This module provides the main backup and restore functionality.
"""

import shutil
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import asyncio
import aiofiles

from .storage import StorageManager, BackupMetadata
from .utils import (
    generate_unique_backup_identifier,
    calculate_file_sha256_checksum,
    validate_and_normalize_file_path,
    copy_file_safely_with_verification,
    BackupOperationProgressTracker
)


class BackupManager:
    """Main backup management class."""

    def __init__(self, storage_manager: Optional[StorageManager] = None):
        """
        Initialize backup manager.

        Args:
            storage_manager: Storage manager instance
        """
        self.storage = storage_manager or StorageManager()
        self.active_operations: Dict[str, BackupOperationProgressTracker] = {}
    
    async def create_file_backup(
        self,
        file_path: Union[str, Path],
        context_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a backup of a single file.
        
        Args:
            file_path: Path to the file to backup
            context_description: Optional description of the backup context
            
        Returns:
            Dictionary with backup information
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be read
        """
        file_path = validate_and_normalize_file_path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Generate backup metadata
        backup_id = generate_unique_backup_identifier()
        timestamp = datetime.now().isoformat()
        file_size = file_path.stat().st_size
        checksum = await calculate_file_sha256_checksum(file_path)
        
        metadata = BackupMetadata(
            backup_id=backup_id,
            original_path=str(file_path),
            timestamp=timestamp,
            file_size=file_size,
            checksum=checksum,
            backup_type="file",
            context_description=context_description,
            status="completed"
        )
        
        # Store the backup
        backup_path = await self.storage.store_individual_file_backup(file_path, metadata)
        
        return {
            "backup_id": backup_id,
            "timestamp": timestamp,
            "file_size": file_size,
            "checksum": checksum,
            "backup_path": str(backup_path)
        }
    
    async def create_folder_backup(
        self,
        folder_path: Union[str, Path],
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        context_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a backup of a folder.
        
        Args:
            folder_path: Path to the folder to backup
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude
            max_depth: Maximum recursion depth
            context_description: Optional description
            
        Returns:
            Dictionary with backup information
        """
        folder_path = validate_and_normalize_file_path(folder_path)

        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        if not folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")

        # Calculate total size
        total_size = sum(
            f.stat().st_size
            for f in folder_path.rglob("*")
            if f.is_file()
        )

        # Generate backup metadata
        backup_id = generate_unique_backup_identifier()
        timestamp = datetime.now().isoformat()
        
        metadata = BackupMetadata(
            backup_id=backup_id,
            original_path=str(folder_path),
            timestamp=timestamp,
            file_size=total_size,
            checksum="",  # Will be calculated after compression
            backup_type="folder",
            context_description=context_description,
            compression="gzip",
            status="completed"
        )
        
        # Store the backup
        backup_path = await self.storage.store_compressed_folder_backup(
            folder_path,
            metadata,
            include_patterns,
            exclude_patterns
        )
        
        return {
            "backup_id": backup_id,
            "timestamp": timestamp,
            "file_size": total_size,
            "backup_path": str(backup_path)
        }
    
    async def restore_file_backup(
        self,
        backup_id: str,
        target_path: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """
        Restore a file backup.
        
        Args:
            backup_id: ID of the backup to restore
            target_path: Optional target path (defaults to original path)
            
        Returns:
            Dictionary with restore information
        """
        # Get backup metadata
        metadata = await self.storage.retrieve_backup_metadata_by_id(backup_id)
        if not metadata:
            raise ValueError(f"Backup not found: {backup_id}")

        if metadata.backup_type != "file":
            raise ValueError(f"Backup {backup_id} is not a file backup")

        # Determine target path
        if target_path is None:
            target_path = Path(metadata.original_path)
        else:
            target_path = validate_and_normalize_file_path(target_path)
        
        # Create safety backup if target exists
        safety_backup_path = None
        if target_path.exists():
            safety_backup_path = await self._create_safety_backup(target_path)
        
        try:
            # Get backup storage info
            global_registry = await self.storage.load_global_backup_registry()
            backup_info = global_registry["backups"][backup_id]
            backup_storage_path = Path(backup_info["storage_path"])

            # Restore the file
            await copy_file_safely_with_verification(backup_storage_path, target_path)

            # Verify checksum
            restored_checksum = await calculate_file_sha256_checksum(target_path)
            if restored_checksum != metadata.checksum:
                raise ValueError("Checksum verification failed after restore")
            
            return {
                "backup_id": backup_id,
                "restored_path": str(target_path),
                "safety_backup": str(safety_backup_path) if safety_backup_path else None,
                "checksum_verified": True
            }
            
        except Exception as e:
            # Restore safety backup if something went wrong
            if safety_backup_path and safety_backup_path.exists():
                await copy_file_safely_with_verification(safety_backup_path, target_path)
            raise e
    
    async def restore_folder_backup(
        self,
        backup_id: str,
        target_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Restore a folder backup.
        
        Args:
            backup_id: ID of the backup to restore
            target_path: Target path for restoration
            
        Returns:
            Dictionary with restore information
        """
        # Get backup metadata
        metadata = await self.storage.retrieve_backup_metadata_by_id(backup_id)
        if not metadata:
            raise ValueError(f"Backup not found: {backup_id}")

        if metadata.backup_type != "folder":
            raise ValueError(f"Backup {backup_id} is not a folder backup")

        target_path = validate_and_normalize_file_path(target_path)
        
        # Create safety backup if target exists
        safety_backup_path = None
        if target_path.exists():
            safety_backup_path = await self._create_safety_backup(target_path)
        
        try:
            # Get backup storage info
            global_registry = await self.storage.load_global_backup_registry()
            backup_info = global_registry["backups"][backup_id]
            backup_storage_path = Path(backup_info["storage_path"])
            
            # Extract the archive
            def extract_archive():
                with tarfile.open(backup_storage_path, "r:gz") as tar:
                    tar.extractall(target_path.parent)
            
            await asyncio.get_event_loop().run_in_executor(None, extract_archive)
            
            return {
                "backup_id": backup_id,
                "restored_path": str(target_path),
                "safety_backup": str(safety_backup_path) if safety_backup_path else None
            }
            
        except Exception as e:
            # Restore safety backup if something went wrong
            if safety_backup_path and safety_backup_path.exists():
                if target_path.is_file():
                    await copy_file_safely_with_verification(safety_backup_path, target_path)
                else:
                    shutil.copytree(safety_backup_path, target_path, dirs_exist_ok=True)
            raise e
    
    async def list_backups_for_path(
        self, 
        file_path: Union[str, Path]
    ) -> List[Dict[str, Any]]:
        """
        List all backups for a specific file or folder.
        
        Args:
            file_path: Path to list backups for
            
        Returns:
            List of backup information dictionaries
        """
        file_path = validate_and_normalize_file_path(file_path)
        backups = await self.storage.list_all_backups_for_specific_path(file_path)
        
        return [
            {
                "backup_id": backup.backup_id,
                "timestamp": backup.timestamp,
                "file_size": backup.file_size,
                "context_description": backup.context_description,
                "backup_type": backup.backup_type,
                "status": backup.status
            }
            for backup in backups
        ]
    
    async def list_all_backups(self) -> List[Dict[str, Any]]:
        """
        List all backups in the system.
        
        Returns:
            List of all backup information dictionaries
        """
        backups = await self.storage.list_all_backups_in_system()
        
        return [
            {
                "backup_id": backup.backup_id,
                "original_path": backup.original_path,
                "timestamp": backup.timestamp,
                "file_size": backup.file_size,
                "context_description": backup.context_description,
                "backup_type": backup.backup_type,
                "status": backup.status
            }
            for backup in backups
        ]
    
    async def _create_safety_backup(self, path: Path) -> Path:
        """Create a safety backup before restore operation."""
        safety_dir = path.parent / ".backup_safety"
        safety_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safety_name = f"{path.name}_{timestamp}"
        safety_path = safety_dir / safety_name
        
        if path.is_file():
            await copy_file_safely_with_verification(path, safety_path)
        else:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: shutil.copytree(path, safety_path)
            )
        
        return safety_path
    
    def cancel_operation(self, operation_id: str) -> bool:
        """
        Cancel an active backup operation.
        
        Args:
            operation_id: ID of the operation to cancel
            
        Returns:
            True if operation was cancelled, False if not found
        """
        if operation_id in self.active_operations:
            self.active_operations[operation_id].cancel()
            return True
        return False
