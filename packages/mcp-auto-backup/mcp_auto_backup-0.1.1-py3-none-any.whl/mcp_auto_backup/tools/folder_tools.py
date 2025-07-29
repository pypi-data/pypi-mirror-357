"""
Folder backup MCP tools.

This module provides MCP tool functions for folder backup operations.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..core.backup import BackupManager
from ..core.storage import StorageManager
from ..config.settings import get_settings


def register_folder_tools(mcp: FastMCP) -> None:
    """Register folder backup tools with the MCP server."""
    
    settings = get_settings()
    storage_manager = StorageManager(settings.backup_root)
    backup_manager = BackupManager(storage_manager)
    
    @mcp.tool()
    async def backup_folder_create(
        folder_path: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        context_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a backup of a folder.
        
        Args:
            folder_path: Path to the folder to backup
            include_patterns: List of glob patterns to include (e.g., ["*.py", "*.txt"])
            exclude_patterns: List of glob patterns to exclude (e.g., ["*.tmp", "__pycache__"])
            max_depth: Maximum recursion depth for folder traversal
            context_description: Optional description of the backup context
            
        Returns:
            Dictionary containing backup_id, timestamp, and total_size
            
        Note:
            If exclude_patterns is not provided, default exclusion patterns will be used
            (temporary files, cache directories, version control folders, etc.)
        """
        try:
            # Use default exclude patterns if none provided
            if exclude_patterns is None:
                exclude_patterns = settings.default_exclude_patterns
            
            result = await backup_manager.create_folder_backup(
                folder_path=folder_path,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                max_depth=max_depth,
                context_description=context_description
            )
            
            return {
                "success": True,
                "backup_id": result["backup_id"],
                "timestamp": result["timestamp"],
                "file_size": result["file_size"],
                "backup_path": result["backup_path"],
                "include_patterns": include_patterns,
                "exclude_patterns": exclude_patterns,
                "max_depth": max_depth,
                "message": f"Successfully created folder backup for {folder_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create folder backup for {folder_path}"
            }
    
    @mcp.tool()
    async def backup_folder_list(folder_path: str) -> Dict[str, Any]:
        """
        List all backups for a specific folder.
        
        Args:
            folder_path: Path to the folder to list backups for
            
        Returns:
            Dictionary containing list of folder backup records
        """
        try:
            backups = await backup_manager.list_backups_for_path(folder_path)
            
            # Filter to only folder backups
            folder_backups = [b for b in backups if b["backup_type"] == "folder"]
            
            return {
                "success": True,
                "folder_path": folder_path,
                "backup_count": len(folder_backups),
                "backups": folder_backups,
                "message": f"Found {len(folder_backups)} folder backup(s) for {folder_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list folder backups for {folder_path}"
            }
    
    @mcp.tool()
    async def backup_folder_restore(
        backup_id: str,
        target_path: str
    ) -> Dict[str, Any]:
        """
        Restore a folder backup.
        
        Args:
            backup_id: ID of the backup to restore
            target_path: Target path where the folder should be restored
            
        Returns:
            Dictionary containing restore information
            
        Note:
            This function automatically creates a safety backup of the existing folder
            before performing the restore operation. The folder will be extracted as
            a compressed archive.
        """
        try:
            result = await backup_manager.restore_folder_backup(
                backup_id=backup_id,
                target_path=target_path
            )
            
            return {
                "success": True,
                "backup_id": result["backup_id"],
                "restored_path": result["restored_path"],
                "safety_backup": result.get("safety_backup"),
                "message": f"Successfully restored folder backup {backup_id} to {target_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to restore folder backup {backup_id}"
            }
