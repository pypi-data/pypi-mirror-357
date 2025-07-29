"""
Storage Management System for MCP Auto Backup

PURPOSE:
    This module provides comprehensive storage management for backup data and metadata,
    handling both file and folder backups with efficient organization and retrieval.

FEATURES:
    - JSON-based metadata storage for fast querying
    - Hierarchical storage organization by file/folder hash
    - Compressed folder backups using tar.gz format
    - Atomic backup operations with rollback capability
    - Global metadata tracking for all backups

STORAGE STRUCTURE:
    .mcp_backups/
    ├── metadata.json              # Global backup registry
    ├── files/                     # Individual file backups
    │   └── {file_hash}/
    │       ├── {backup_id}.data   # Actual backup data
    │       └── {backup_id}.meta   # Backup metadata
    └── folders/                   # Folder backups
        └── {folder_hash}/
            ├── {backup_id}.tar.gz # Compressed folder backup
            └── {backup_id}.meta   # Backup metadata

USAGE:
    Primary interface for AI agents to store and retrieve backup data.
    Handles all low-level storage operations and metadata management.

PERFORMANCE:
    - Async I/O for large file operations
    - Efficient hash-based organization
    - Minimal memory footprint for metadata operations
"""

import json
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import aiofiles
import asyncio

from .utils import (
    generate_unique_backup_identifier,
    generate_file_path_storage_key,
    copy_file_safely_with_verification
)


class BackupMetadata:
    """
    Comprehensive metadata container for backup operations.

    PURPOSE:
        Stores all essential information about a backup including identification,
        timing, integrity verification, and operational context.

    ATTRIBUTES:
        - backup_id: Unique identifier for the backup
        - original_path: Source file/folder path that was backed up
        - timestamp: ISO format timestamp of backup creation
        - file_size: Total size in bytes of backed up data
        - checksum: SHA256 hash for integrity verification
        - backup_type: "file" or "folder" to indicate backup type
        - context_description: Optional human-readable backup context
        - compression: Compression method used ("none", "gzip", etc.)
        - status: Current backup status ("completed", "in_progress", "failed")

    USAGE:
        Used by StorageManager to track backup information and by AI agents
        to understand backup characteristics and status.
    """

    def __init__(
        self,
        backup_id: str,
        original_path: str,
        timestamp: str,
        file_size: int,
        checksum: str,
        backup_type: str = "file",
        context_description: Optional[str] = None,
        compression: str = "none",
        status: str = "completed"
    ):
        self.backup_id = backup_id
        self.original_path = original_path
        self.timestamp = timestamp
        self.file_size = file_size
        self.checksum = checksum
        self.backup_type = backup_type
        self.context_description = context_description
        self.compression = compression
        self.status = status
    
    def convert_to_json_serializable_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to dictionary format for JSON storage.

        PURPOSE:
            Transforms the metadata object into a dictionary that can be
            safely serialized to JSON for persistent storage.

        Returns:
            Dict[str, Any]: Dictionary containing all metadata fields

        USAGE:
            Used by StorageManager when saving metadata to .meta files
        """
        return {
            "backup_id": self.backup_id,
            "original_path": self.original_path,
            "timestamp": self.timestamp,
            "file_size": self.file_size,
            "checksum": self.checksum,
            "backup_type": self.backup_type,
            "context_description": self.context_description,
            "compression": self.compression,
            "status": self.status
        }

    @classmethod
    def create_from_json_dict(cls, metadata_dict: Dict[str, Any]) -> "BackupMetadata":
        """
        Create BackupMetadata instance from dictionary data.

        PURPOSE:
            Reconstructs metadata object from JSON data loaded from storage.

        Args:
            metadata_dict (Dict[str, Any]): Dictionary containing metadata fields

        Returns:
            BackupMetadata: New instance with data from dictionary

        USAGE:
            Used by StorageManager when loading metadata from .meta files
        """
        return cls(**metadata_dict)


class StorageManager:
    """
    Comprehensive backup storage management system.

    PURPOSE:
        Handles all aspects of backup storage including directory organization,
        metadata management, file operations, and data retrieval for the MCP backup system.

    RESPONSIBILITIES:
        - Create and maintain backup directory structure
        - Store and retrieve backup data and metadata
        - Manage global backup registry
        - Handle file and folder backup operations
        - Provide backup listing and search capabilities

    STORAGE ORGANIZATION:
        - Files organized by hash of original path
        - Separate directories for file vs folder backups
        - JSON metadata for fast querying
        - Compressed archives for folder backups

    USAGE:
        Primary storage interface used by BackupManager and MCP tools.
        AI agents interact with this through higher-level backup operations.
    """

    def __init__(self, backup_root_directory: Optional[Union[str, Path]] = None):
        """
        Initialize storage manager with backup directory structure.

        PURPOSE:
            Sets up the storage system with proper directory hierarchy
            and ensures all required directories exist.

        Args:
            backup_root_directory (Optional[Union[str, Path]]):
                Root directory for all backup storage (default: .mcp_backups in current directory)

        DIRECTORY STRUCTURE CREATED:
            backup_root/
            ├── metadata.json    # Global backup registry
            ├── files/          # Individual file backups
            └── folders/        # Folder backups
        """
        if backup_root_directory is None:
            backup_root_directory = Path.cwd() / ".mcp_backups"

        self.backup_root = Path(backup_root_directory)
        self.files_storage_directory = self.backup_root / "files"
        self.folders_storage_directory = self.backup_root / "folders"
        self.global_metadata_file = self.backup_root / "metadata.json"

        # Ensure all required directories exist
        self.backup_root.mkdir(exist_ok=True)
        self.files_storage_directory.mkdir(exist_ok=True)
        self.folders_storage_directory.mkdir(exist_ok=True)
    
    async def load_global_backup_registry(self) -> Dict[str, Any]:
        """
        Load the global backup registry from persistent storage.

        PURPOSE:
            Retrieves the master index of all backups in the system,
            providing fast access to backup information without scanning directories.

        Returns:
            Dict[str, Any]: Global metadata containing:
                - "backups": Dictionary of all backup records indexed by backup_id
                - "last_updated": ISO timestamp of last registry update

        BEHAVIOR:
            - Creates default registry if file doesn't exist
            - Returns empty registry with current timestamp for new installations
        """
        if not self.global_metadata_file.exists():
            return {"backups": {}, "last_updated": datetime.now().isoformat()}

        async with aiofiles.open(self.global_metadata_file, 'r') as metadata_file:
            file_content = await metadata_file.read()
            return json.loads(file_content)

    async def save_global_backup_registry(self, registry_data: Dict[str, Any]) -> None:
        """
        Save the global backup registry to persistent storage.

        PURPOSE:
            Persists the master backup index to disk with automatic timestamp update.

        Args:
            registry_data (Dict[str, Any]): Complete registry data to save

        BEHAVIOR:
            - Automatically updates "last_updated" timestamp
            - Writes formatted JSON for human readability
            - Ensures atomic write operation
        """
        registry_data["last_updated"] = datetime.now().isoformat()

        async with aiofiles.open(self.global_metadata_file, 'w') as metadata_file:
            formatted_json = json.dumps(registry_data, indent=2)
            await metadata_file.write(formatted_json)
    
    async def store_individual_file_backup(
        self,
        source_file_path: Path,
        backup_metadata_info: BackupMetadata
    ) -> Path:
        """
        Store a complete backup of an individual file with metadata.

        PURPOSE:
            Creates a persistent backup copy of a single file along with its metadata,
            organizing storage by file path hash for efficient retrieval.

        Args:
            source_file_path (Path): Path to the original file to backup
            backup_metadata_info (BackupMetadata): Complete metadata for this backup

        Returns:
            Path: Location where the backup data file was stored

        STORAGE PROCESS:
            1. Generate hash-based storage directory from file path
            2. Copy source file to backup storage location
            3. Save metadata as separate .meta file
            4. Update global backup registry

        ORGANIZATION:
            files/{file_path_hash}/{backup_id}.data  # Actual file backup
            files/{file_path_hash}/{backup_id}.meta  # Backup metadata
        """
        # Generate storage directory based on file path hash
        file_path_hash = generate_file_path_storage_key(source_file_path)
        backup_storage_directory = self.files_storage_directory / file_path_hash
        backup_storage_directory.mkdir(exist_ok=True)

        # Store the actual backup data
        backup_data_file_path = backup_storage_directory / f"{backup_metadata_info.backup_id}.data"
        await copy_file_safely_with_verification(source_file_path, backup_data_file_path)

        # Store backup metadata as JSON
        metadata_file_path = backup_storage_directory / f"{backup_metadata_info.backup_id}.meta"
        async with aiofiles.open(metadata_file_path, 'w') as metadata_file:
            metadata_json = json.dumps(backup_metadata_info.convert_to_json_serializable_dict(), indent=2)
            await metadata_file.write(metadata_json)

        # Update global backup registry
        global_registry = await self.load_global_backup_registry()
        global_registry["backups"][backup_metadata_info.backup_id] = {
            "type": "file",
            "original_path": str(source_file_path),
            "storage_path": str(backup_data_file_path),
            "metadata_path": str(metadata_file_path),
            "timestamp": backup_metadata_info.timestamp
        }
        await self.save_global_backup_registry(global_registry)

        return backup_data_file_path
    
    async def store_compressed_folder_backup(
        self,
        source_folder_path: Path,
        backup_metadata_info: BackupMetadata,
        include_file_patterns: Optional[List[str]] = None,
        exclude_file_patterns: Optional[List[str]] = None
    ) -> Path:
        """
        Store a complete folder backup as a compressed archive with metadata.

        PURPOSE:
            Creates a compressed backup of an entire folder structure, preserving
            directory hierarchy and file relationships while minimizing storage space.

        Args:
            source_folder_path (Path): Path to the folder to backup
            backup_metadata_info (BackupMetadata): Complete metadata for this backup
            include_file_patterns (Optional[List[str]]): Glob patterns for files to include
            exclude_file_patterns (Optional[List[str]]): Glob patterns for files to exclude

        Returns:
            Path: Location where the compressed backup archive was stored

        COMPRESSION:
            - Uses tar.gz format for cross-platform compatibility
            - Preserves file permissions and timestamps
            - Maintains directory structure

        STORAGE PROCESS:
            1. Generate hash-based storage directory from folder path
            2. Create compressed tar.gz archive of folder contents
            3. Save metadata as separate .meta file
            4. Update global backup registry

        ORGANIZATION:
            folders/{folder_path_hash}/{backup_id}.tar.gz  # Compressed backup
            folders/{folder_path_hash}/{backup_id}.meta    # Backup metadata
        """
        # Generate storage directory based on folder path hash
        folder_path_hash = generate_file_path_storage_key(source_folder_path)
        backup_storage_directory = self.folders_storage_directory / folder_path_hash
        backup_storage_directory.mkdir(exist_ok=True)

        # Create compressed backup archive
        backup_archive_file_path = backup_storage_directory / f"{backup_metadata_info.backup_id}.tar.gz"

        def create_compressed_archive():
            """Create tar.gz archive of the folder in thread pool."""
            with tarfile.open(backup_archive_file_path, "w:gz") as archive:
                archive.add(source_folder_path, arcname=source_folder_path.name)

        # Run compression in thread pool to avoid blocking the event loop
        await asyncio.get_event_loop().run_in_executor(None, create_compressed_archive)

        # Store backup metadata as JSON
        metadata_file_path = backup_storage_directory / f"{backup_metadata_info.backup_id}.meta"
        async with aiofiles.open(metadata_file_path, 'w') as metadata_file:
            metadata_json = json.dumps(backup_metadata_info.convert_to_json_serializable_dict(), indent=2)
            await metadata_file.write(metadata_json)

        # Update global backup registry
        global_registry = await self.load_global_backup_registry()
        global_registry["backups"][backup_metadata_info.backup_id] = {
            "type": "folder",
            "original_path": str(source_folder_path),
            "storage_path": str(backup_archive_file_path),
            "metadata_path": str(metadata_file_path),
            "timestamp": backup_metadata_info.timestamp
        }
        await self.save_global_backup_registry(global_registry)

        return backup_archive_file_path
    
    async def retrieve_backup_metadata_by_id(self, backup_identifier: str) -> Optional[BackupMetadata]:
        """
        Retrieve complete backup metadata for a specific backup ID.

        PURPOSE:
            Loads detailed backup information from storage for use in restore
            operations and backup management tasks.

        Args:
            backup_identifier (str): Unique backup ID to retrieve metadata for

        Returns:
            Optional[BackupMetadata]: Complete metadata object if found, None if not found

        PROCESS:
            1. Check global registry for backup existence
            2. Load metadata from corresponding .meta file
            3. Reconstruct BackupMetadata object from JSON data

        USAGE:
            Used by restore operations and backup listing functions to get
            detailed information about specific backups.
        """
        global_registry = await self.load_global_backup_registry()
        backup_registry_entry = global_registry["backups"].get(backup_identifier)

        if not backup_registry_entry:
            return None

        metadata_file_path = Path(backup_registry_entry["metadata_path"])
        if not metadata_file_path.exists():
            return None

        async with aiofiles.open(metadata_file_path, 'r') as metadata_file:
            metadata_content = await metadata_file.read()
            metadata_dictionary = json.loads(metadata_content)
            return BackupMetadata.create_from_json_dict(metadata_dictionary)
    
    async def list_all_backups_for_specific_path(self, target_file_or_folder_path: Path) -> List[BackupMetadata]:
        """
        List all backups associated with a specific file or folder path.

        PURPOSE:
            Retrieves all backup instances for a given path, allowing AI agents
            to see backup history and choose specific versions for restoration.

        Args:
            target_file_or_folder_path (Path): Path to list backups for

        Returns:
            List[BackupMetadata]: All backups for the path, sorted by timestamp (newest first)

        SEARCH PROCESS:
            1. Generate storage key from path
            2. Check both file and folder backup directories
            3. Load metadata from all found .meta files
            4. Sort results by creation timestamp
        """
        path_storage_key = generate_file_path_storage_key(target_file_or_folder_path)
        backup_list = []

        # Check file backups directory
        file_backup_directory = self.files_storage_directory / path_storage_key
        if file_backup_directory.exists():
            for metadata_file in file_backup_directory.glob("*.meta"):
                async with aiofiles.open(metadata_file, 'r') as file_handle:
                    metadata_content = await file_handle.read()
                    metadata_dict = json.loads(metadata_content)
                    backup_list.append(BackupMetadata.create_from_json_dict(metadata_dict))

        # Check folder backups directory
        folder_backup_directory = self.folders_storage_directory / path_storage_key
        if folder_backup_directory.exists():
            for metadata_file in folder_backup_directory.glob("*.meta"):
                async with aiofiles.open(metadata_file, 'r') as file_handle:
                    metadata_content = await file_handle.read()
                    metadata_dict = json.loads(metadata_content)
                    backup_list.append(BackupMetadata.create_from_json_dict(metadata_dict))

        # Sort by timestamp (newest first)
        backup_list.sort(key=lambda backup: backup.timestamp, reverse=True)
        return backup_list
    
    async def list_all_backups_in_system(self) -> List[BackupMetadata]:
        """
        Retrieve complete list of all backups in the entire system.

        PURPOSE:
            Provides comprehensive overview of all backup operations for system
            monitoring, cleanup operations, and global backup management.

        Returns:
            List[BackupMetadata]: All backups in the system, sorted by timestamp (newest first)

        PROCESS:
            1. Load global backup registry
            2. Retrieve detailed metadata for each backup
            3. Filter out any corrupted or missing backups
            4. Sort by creation timestamp for chronological view

        USAGE:
            Used by AI agents for backup overview, cleanup operations,
            and system status reporting.
        """
        global_registry = await self.load_global_backup_registry()
        complete_backup_list = []

        for backup_identifier, registry_entry in global_registry["backups"].items():
            backup_metadata = await self.retrieve_backup_metadata_by_id(backup_identifier)
            if backup_metadata:
                complete_backup_list.append(backup_metadata)

        # Sort by timestamp (newest first)
        complete_backup_list.sort(key=lambda backup: backup.timestamp, reverse=True)
        return complete_backup_list
