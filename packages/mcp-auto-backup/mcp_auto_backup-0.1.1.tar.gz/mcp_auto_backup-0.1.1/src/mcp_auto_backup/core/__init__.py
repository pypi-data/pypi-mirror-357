"""
Core backup functionality for MCP Auto Backup.

This module provides the core backup and restore functionality,
including storage management and utility functions.
"""

from .backup import BackupManager
from .storage import StorageManager
from .utils import (
    generate_unique_backup_identifier,
    calculate_file_sha256_checksum,
    validate_and_normalize_file_path,
    format_bytes_to_human_readable,
    copy_file_safely_with_verification,
    detect_if_file_is_binary,
    generate_file_path_storage_key,
    BackupOperationProgressTracker
)

__all__ = [
    "BackupManager",
    "StorageManager",
    "generate_unique_backup_identifier",
    "calculate_file_sha256_checksum",
    "validate_and_normalize_file_path",
    "format_bytes_to_human_readable",
    "copy_file_safely_with_verification",
    "detect_if_file_is_binary",
    "generate_file_path_storage_key",
    "BackupOperationProgressTracker",
]
