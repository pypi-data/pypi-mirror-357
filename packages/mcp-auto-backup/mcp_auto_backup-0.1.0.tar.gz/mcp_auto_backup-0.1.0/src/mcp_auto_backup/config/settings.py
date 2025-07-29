"""
Settings and configuration for MCP Auto Backup.

This module provides configuration management using Pydantic.
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic import BaseSettings, Field


class BackupSettings(BaseSettings):
    """Configuration settings for MCP Auto Backup."""
    
    # Storage settings
    backup_root: Path = Field(
        default_factory=lambda: Path.cwd() / ".mcp_backups",
        description="Root directory for storing backups"
    )
    
    # Security settings
    enable_encryption: bool = Field(
        default=False,
        description="Enable backup encryption"
    )
    
    encryption_key: Optional[str] = Field(
        default=None,
        description="Encryption key for backups"
    )
    
    # Performance settings
    max_file_size: int = Field(
        default=100 * 1024 * 1024,  # 100MB
        description="Maximum file size for backup (bytes)"
    )
    
    chunk_size: int = Field(
        default=8192,
        description="Chunk size for file operations (bytes)"
    )
    
    max_concurrent_operations: int = Field(
        default=3,
        description="Maximum concurrent backup operations"
    )
    
    # Backup behavior settings
    auto_cleanup_days: int = Field(
        default=30,
        description="Days to keep backups before auto-cleanup (0 = disabled)"
    )
    
    create_safety_backups: bool = Field(
        default=True,
        description="Create safety backups before restore operations"
    )
    
    verify_checksums: bool = Field(
        default=True,
        description="Verify file checksums after backup/restore"
    )
    
    # Default patterns
    default_exclude_patterns: List[str] = Field(
        default_factory=lambda: [
            "*.tmp",
            "*.log",
            "__pycache__",
            ".git",
            ".svn",
            "node_modules",
            ".DS_Store",
            "Thumbs.db"
        ],
        description="Default patterns to exclude from folder backups"
    )
    
    # Logging settings
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    log_file: Optional[Path] = Field(
        default=None,
        description="Log file path (None = console only)"
    )
    
    # MCP Server settings
    server_name: str = Field(
        default="MCP Auto Backup",
        description="MCP server name"
    )
    
    server_version: str = Field(
        default="0.1.0",
        description="MCP server version"
    )
    
    class Config:
        env_prefix = "MCP_BACKUP_"
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings: Optional[BackupSettings] = None


def get_settings() -> BackupSettings:
    """
    Get the global settings instance.
    
    Returns:
        BackupSettings instance
    """
    global _settings
    if _settings is None:
        _settings = BackupSettings()
    return _settings


def update_settings(**kwargs) -> BackupSettings:
    """
    Update global settings with new values.
    
    Args:
        **kwargs: Settings to update
        
    Returns:
        Updated BackupSettings instance
    """
    global _settings
    if _settings is None:
        _settings = BackupSettings(**kwargs)
    else:
        for key, value in kwargs.items():
            if hasattr(_settings, key):
                setattr(_settings, key, value)
    return _settings


def reset_settings() -> BackupSettings:
    """
    Reset settings to defaults.
    
    Returns:
        New BackupSettings instance with defaults
    """
    global _settings
    _settings = BackupSettings()
    return _settings
