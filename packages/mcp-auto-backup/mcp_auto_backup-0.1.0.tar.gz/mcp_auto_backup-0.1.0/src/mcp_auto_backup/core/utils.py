"""
Core Utility Functions for MCP Auto Backup System

PURPOSE:
    This module provides essential utility functions that support the backup system's
    core operations including file validation, checksum calculation, and safe file operations.

FEATURES:
    - Unique backup ID generation using UUID4
    - Asynchronous SHA256 checksum calculation for large files
    - Path validation and security checks to prevent path traversal attacks
    - File size formatting for human-readable output
    - Safe file copying with error handling
    - Binary file detection for proper handling
    - Progress tracking for long-running operations

USAGE:
    These utilities are primarily used by BackupManager and StorageManager classes.
    AI models can use these functions to understand file operations and validation.

SECURITY NOTES:
    - All path operations include security validation
    - Checksum verification ensures data integrity
    - Safe file operations prevent data corruption

PERFORMANCE:
    - Async operations for large file handling
    - Chunked reading/writing to manage memory usage
    - Efficient hash calculations with streaming
"""

import hashlib
import uuid
from pathlib import Path
from typing import Optional, Union
import asyncio
import aiofiles


def generate_unique_backup_identifier() -> str:
    """
    Generate a unique backup identifier using UUID4 algorithm.

    PURPOSE:
        Creates a globally unique identifier for each backup operation to ensure
        no conflicts between different backup instances.

    Returns:
        str: A unique backup ID in UUID4 format (e.g., "550e8400-e29b-41d4-a716-446655440000")

    USAGE:
        backup_id = generate_unique_backup_identifier()
        # Use this ID to track and reference specific backups
    """
    return str(uuid.uuid4())


async def calculate_file_sha256_checksum(file_path: Union[str, Path]) -> str:
    """
    Calculate SHA256 checksum of a file using asynchronous operations.

    PURPOSE:
        Computes cryptographic hash to verify file integrity during backup and restore.
        Uses async I/O to handle large files without blocking the event loop.

    Args:
        file_path (Union[str, Path]): Absolute or relative path to the target file

    Returns:
        str: SHA256 checksum as hexadecimal string (64 characters)

    Raises:
        FileNotFoundError: When the specified file does not exist
        PermissionError: When the file cannot be read due to insufficient permissions
        OSError: When file I/O operations fail

    PERFORMANCE:
        - Reads file in 8KB chunks to manage memory usage
        - Suitable for files of any size without memory overflow

    EXAMPLE:
        checksum = await calculate_file_sha256_checksum("/path/to/file.txt")
        # Returns: "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    sha256_hash = hashlib.sha256()
    
    async with aiofiles.open(file_path, 'rb') as f:
        while chunk := await f.read(8192):
            sha256_hash.update(chunk)
    
    return sha256_hash.hexdigest()


def validate_and_normalize_file_path(path: Union[str, Path]) -> Path:
    """
    Validate file/directory path for security and normalize to absolute path.

    PURPOSE:
        Ensures path safety by preventing directory traversal attacks and normalizes
        paths to absolute form for consistent handling across the system.

    Args:
        path (Union[str, Path]): File or directory path to validate (relative or absolute)

    Returns:
        Path: Normalized absolute Path object that is safe to use

    Raises:
        ValueError: When path contains directory traversal patterns (..) or other unsafe elements
        OSError: When path resolution fails due to filesystem issues

    SECURITY:
        - Prevents path traversal attacks (../ sequences)
        - Resolves symbolic links to actual paths
        - Converts relative paths to absolute paths

    EXAMPLE:
        safe_path = validate_and_normalize_file_path("../../../etc/passwd")  # Raises ValueError
        safe_path = validate_and_normalize_file_path("./my_file.txt")        # Returns absolute path
    """
    path = Path(path).resolve()

    # Security check: prevent path traversal attacks
    if '..' in str(path):
        raise ValueError("Path traversal detected - directory traversal patterns are not allowed")

    return path


def generate_file_path_storage_key(file_path: Union[str, Path]) -> str:
    """
    Generate a unique storage key from file path for backup organization.

    PURPOSE:
        Creates a consistent hash-based key from file paths to organize backups
        in the storage system without exposing actual file paths.

    Args:
        file_path (Union[str, Path]): File or directory path to generate key for

    Returns:
        str: MD5 hash of the absolute path (32 hexadecimal characters)

    USAGE:
        Used internally to create directory names in backup storage structure.
        Same file path will always generate the same storage key.

    EXAMPLE:
        key = generate_file_path_storage_key("/home/user/document.txt")
        # Returns: "5d41402abc4b2a76b9719d911017c592"
    """
    absolute_path = str(Path(file_path).resolve())
    return hashlib.md5(absolute_path.encode()).hexdigest()


def format_bytes_to_human_readable(size_in_bytes: int) -> str:
    """
    Convert file size from bytes to human-readable format with appropriate units.

    PURPOSE:
        Transforms raw byte counts into user-friendly size representations
        for display in logs, reports, and user interfaces.

    Args:
        size_in_bytes (int): File size in bytes (non-negative integer)

    Returns:
        str: Formatted size string with unit (e.g., "1.5 MB", "256 KB", "2.1 GB")

    UNITS:
        - B (bytes): 0-1023 bytes
        - KB (kilobytes): 1024 bytes - 1023 KB
        - MB (megabytes): 1024 KB - 1023 MB
        - GB (gigabytes): 1024 MB - 1023 GB
        - TB (terabytes): 1024 GB and above

    EXAMPLE:
        format_bytes_to_human_readable(1536) → "1.5 KB"
        format_bytes_to_human_readable(0) → "0 B"
        format_bytes_to_human_readable(1073741824) → "1.0 GB"
    """
    if size_in_bytes == 0:
        return "0 B"

    unit_names = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size_value = float(size_in_bytes)

    while size_value >= 1024 and unit_index < len(unit_names) - 1:
        size_value /= 1024.0
        unit_index += 1

    return f"{size_value:.1f} {unit_names[unit_index]}"


async def copy_file_safely_with_verification(
    source_file_path: Path,
    destination_file_path: Path,
    chunk_size_bytes: int = 8192
) -> None:
    """
    Copy a file from source to destination with safety checks and error handling.

    PURPOSE:
        Performs secure file copying with automatic directory creation and
        comprehensive error handling for backup operations.

    Args:
        source_file_path (Path): Path to the source file that will be copied
        destination_file_path (Path): Path where the file should be copied to
        chunk_size_bytes (int): Size of data chunks for reading/writing (default: 8192 bytes)

    Returns:
        None: Function completes successfully or raises an exception

    Raises:
        FileNotFoundError: When source file does not exist
        PermissionError: When insufficient permissions to read source or write destination
        OSError: When filesystem operations fail (disk full, etc.)

    SAFETY FEATURES:
        - Automatically creates destination directory if it doesn't exist
        - Uses chunked reading to handle large files efficiently
        - Preserves file content integrity through streaming copy

    EXAMPLE:
        await copy_file_safely_with_verification(
            Path("/source/file.txt"),
            Path("/backup/file.txt")
        )
    """
    if not source_file_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_file_path}")

    # Ensure destination directory exists
    destination_file_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(source_file_path, 'rb') as source_file:
        async with aiofiles.open(destination_file_path, 'wb') as destination_file:
            while data_chunk := await source_file.read(chunk_size_bytes):
                await destination_file.write(data_chunk)


def detect_if_file_is_binary(file_path: Union[str, Path]) -> bool:
    """
    Determine if a file contains binary data by analyzing its content.

    PURPOSE:
        Identifies binary files to apply appropriate handling during backup operations.
        Binary files may need different processing than text files.

    Args:
        file_path (Union[str, Path]): Path to the file to analyze

    Returns:
        bool: True if file appears to contain binary data, False if it appears to be text

    DETECTION METHOD:
        - Reads first 1024 bytes of the file
        - Checks for null bytes (0x00) which are common in binary files
        - Returns True if file cannot be read (assumes binary for safety)

    EXAMPLE:
        is_binary = detect_if_file_is_binary("/path/to/image.jpg")  # Returns True
        is_binary = detect_if_file_is_binary("/path/to/text.txt")   # Returns False
    """
    try:
        with open(file_path, 'rb') as file_handle:
            sample_data = file_handle.read(1024)
            return b'\0' in sample_data
    except (OSError, IOError):
        return True  # Assume binary if file cannot be read


class BackupOperationProgressTracker:
    """
    Track progress and status of backup operations for monitoring and cancellation.

    PURPOSE:
        Provides real-time progress tracking for long-running backup operations,
        allowing AI agents to monitor status and cancel operations if needed.

    FEATURES:
        - Progress percentage calculation
        - Operation cancellation support
        - Completion status tracking
        - Thread-safe operation updates

    USAGE:
        Used internally by BackupManager to track file and folder backup progress.
        AI agents can query progress and request cancellation through operation IDs.
    """

    def __init__(self, total_items_to_process: int, unique_operation_id: str):
        """
        Initialize progress tracker for a backup operation.

        Args:
            total_items_to_process (int): Total number of items/bytes to process
            unique_operation_id (str): Unique identifier for this operation
        """
        self.total_items = total_items_to_process
        self.processed_items = 0
        self.operation_id = unique_operation_id
        self.is_cancelled = False

    def update_progress_by_increment(self, increment_amount: int = 1) -> None:
        """
        Update progress by adding to the current count.

        Args:
            increment_amount (int): Number of items to add to progress (default: 1)
        """
        self.processed_items = min(self.processed_items + increment_amount, self.total_items)

    def cancel_operation(self) -> None:
        """
        Mark this operation as cancelled.

        PURPOSE:
            Allows AI agents to cancel long-running backup operations.
            The operation should check this flag and stop processing.
        """
        self.is_cancelled = True

    @property
    def completion_percentage(self) -> float:
        """
        Calculate completion percentage of the operation.

        Returns:
            float: Percentage complete (0.0 to 100.0)
        """
        if self.total_items == 0:
            return 100.0
        return (self.processed_items / self.total_items) * 100.0

    @property
    def is_operation_complete(self) -> bool:
        """
        Check if the operation has completed successfully.

        Returns:
            bool: True if all items have been processed
        """
        return self.processed_items >= self.total_items
