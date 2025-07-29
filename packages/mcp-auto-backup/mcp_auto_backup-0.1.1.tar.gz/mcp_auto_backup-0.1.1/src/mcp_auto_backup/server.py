"""
MCP Auto Backup Server.

This module provides the main MCP server implementation for the backup tool.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .config.settings import get_settings
from .tools.file_tools import register_file_tools
from .tools.folder_tools import register_folder_tools


def setup_logging(settings) -> None:
    """Setup logging configuration."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler if specified
    if settings.log_file:
        log_file = Path(settings.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True
    )


def create_mcp_server() -> FastMCP:
    """
    Create and configure the MCP server.
    
    Returns:
        Configured FastMCP server instance
    """
    settings = get_settings()
    
    # Setup logging
    setup_logging(settings)
    logger = logging.getLogger(__name__)
    
    # Create MCP server
    mcp = FastMCP(
        name=settings.server_name,
        dependencies=[
            "mcp>=1.0.0",
            "click>=8.0.0", 
            "pydantic>=2.0.0",
            "aiofiles>=23.0.0",
            "cryptography>=41.0.0",
        ]
    )
    
    # Ensure backup directory exists
    settings.backup_root.mkdir(parents=True, exist_ok=True)
    logger.info(f"Backup root directory: {settings.backup_root}")
    
    # Register tools
    register_file_tools(mcp)
    register_folder_tools(mcp)
    
    logger.info(f"MCP Auto Backup Server initialized")
    logger.info(f"Server name: {settings.server_name}")
    logger.info(f"Server version: {settings.server_version}")
    
    # Add server information as a resource
    @mcp.resource("server://info")
    def get_server_info() -> str:
        """Get server information and configuration."""
        info = {
            "name": settings.server_name,
            "version": settings.server_version,
            "backup_root": str(settings.backup_root),
            "max_file_size": settings.max_file_size,
            "encryption_enabled": settings.enable_encryption,
            "auto_cleanup_days": settings.auto_cleanup_days,
            "available_tools": [
                "backup_create",
                "backup_list", 
                "backup_restore",
                "backup_folder_create",
                "backup_folder_list",
                "backup_folder_restore",
                "backup_list_all",
                "backup_cancel"
            ]
        }
        return f"MCP Auto Backup Server\n\nConfiguration:\n{info}"
    
    # Add help resource
    @mcp.resource("help://usage")
    def get_usage_help() -> str:
        """Get usage help and examples."""
        help_text = """
MCP Auto Backup - Usage Guide

AVAILABLE TOOLS:

1. backup_create(file_path, context_description=None)
   - Create a backup of a single file
   - Returns: backup_id, timestamp, file_size, checksum

2. backup_list(file_path)
   - List all backups for a specific file
   - Returns: list of backup records

3. backup_restore(backup_id, target_path=None)
   - Restore a file backup (creates safety backup first)
   - Returns: restore information

4. backup_folder_create(folder_path, include_patterns=None, exclude_patterns=None, max_depth=None, context_description=None)
   - Create a backup of a folder with optional filtering
   - Returns: backup_id, timestamp, total_size

5. backup_folder_list(folder_path)
   - List all backups for a specific folder
   - Returns: list of folder backup records

6. backup_folder_restore(backup_id, target_path)
   - Restore a folder backup (creates safety backup first)
   - Returns: restore information

7. backup_list_all()
   - List all backups in the system
   - Returns: comprehensive backup overview

8. backup_cancel(operation_id)
   - Cancel an active backup operation
   - Returns: cancellation status

EXAMPLES:

# Backup a single file
backup_create("/path/to/file.txt", "Before major changes")

# List backups for a file
backup_list("/path/to/file.txt")

# Restore a backup
backup_restore("backup-id-here")

# Backup a folder with exclusions
backup_folder_create("/path/to/project", exclude_patterns=["*.tmp", "__pycache__"])

# List all backups
backup_list_all()

FEATURES:
- Automatic checksum verification
- Safety backups before restore
- Compressed folder backups
- Cross-platform compatibility
- Async operations for large files
"""
        return help_text
    
    return mcp


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        mcp = create_mcp_server()
        mcp.run("stdio")
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Server shutdown requested")
    except Exception as e:
        logging.getLogger(__name__).error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
