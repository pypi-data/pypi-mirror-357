"""
MCP Auto Backup - A lightweight backup tool for AI Agents.

This package provides a Model Context Protocol (MCP) server for backup operations,
designed to be simpler than Git and focused on quick backup needs for AI agents.

Features:
- Single file and folder backup
- Automatic checksum verification
- Safety backups before restore
- Compressed folder backups
- Cross-platform compatibility
- Async operations for large files
"""

__version__ = "0.1.0"
__author__ = "MCP Auto Backup Team"
__email__ = "contact@example.com"

from .server import create_mcp_server, main
from .core import BackupManager, StorageManager
from .config import BackupSettings, get_settings

__all__ = [
    "create_mcp_server",
    "main",
    "BackupManager",
    "StorageManager",
    "BackupSettings",
    "get_settings",
]