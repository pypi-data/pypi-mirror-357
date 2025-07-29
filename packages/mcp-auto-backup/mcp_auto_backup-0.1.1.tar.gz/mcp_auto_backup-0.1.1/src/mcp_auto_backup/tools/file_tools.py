"""
File backup MCP tools.

This module provides MCP tool functions for single file backup operations.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..core.backup import BackupManager
from ..core.storage import StorageManager
from ..config.settings import get_settings


def register_file_tools(mcp: FastMCP) -> None:
    """Register file backup tools with the MCP server."""
    
    settings = get_settings()
    storage_manager = StorageManager(settings.backup_root)
    backup_manager = BackupManager(storage_manager)
    
    @mcp.tool()
    async def backup_create(
        file_path: str, 
        context_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a backup of a single file.
        
        Args:
            file_path: Path to the file to backup
            context_description: Optional description of the backup context
            
        Returns:
            Dictionary containing backup_id, timestamp, file_size, and checksum
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If the file can't be read
            ValueError: If the path is not a file
        """
        try:
            result = await backup_manager.create_file_backup(
                file_path=file_path,
                context_description=context_description
            )
            return {
                "success": True,
                "backup_id": result["backup_id"],
                "timestamp": result["timestamp"],
                "file_size": result["file_size"],
                "checksum": result["checksum"],
                "message": f"Successfully created backup for {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create backup for {file_path}"
            }
    
    @mcp.tool()
    async def backup_list(file_path: str) -> Dict[str, Any]:
        """
        List all backups for a specific file.
        
        Args:
            file_path: Path to the file to list backups for
            
        Returns:
            Dictionary containing list of backup records
        """
        try:
            backups = await backup_manager.list_backups_for_path(file_path)
            return {
                "success": True,
                "file_path": file_path,
                "backup_count": len(backups),
                "backups": backups,
                "message": f"Found {len(backups)} backup(s) for {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list backups for {file_path}"
            }
    
    @mcp.tool()
    async def backup_restore(
        backup_id: str, 
        target_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Restore a file backup.
        
        Args:
            backup_id: ID of the backup to restore
            target_path: Optional target path (defaults to original path)
            
        Returns:
            Dictionary containing restore information
            
        Note:
            This function automatically creates a safety backup of the existing file
            before performing the restore operation.
        """
        try:
            result = await backup_manager.restore_file_backup(
                backup_id=backup_id,
                target_path=target_path
            )
            return {
                "success": True,
                "backup_id": result["backup_id"],
                "restored_path": result["restored_path"],
                "safety_backup": result.get("safety_backup"),
                "checksum_verified": result.get("checksum_verified", False),
                "message": f"Successfully restored backup {backup_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to restore backup {backup_id}"
            }
    
    @mcp.tool()
    async def backup_list_all() -> Dict[str, Any]:
        """
        List all backups in the system.
        
        Returns:
            Dictionary containing all backup records
        """
        try:
            backups = await backup_manager.list_all_backups()
            
            # Group by backup type for better organization
            file_backups = [b for b in backups if b["backup_type"] == "file"]
            folder_backups = [b for b in backups if b["backup_type"] == "folder"]
            
            return {
                "success": True,
                "total_backups": len(backups),
                "file_backups": len(file_backups),
                "folder_backups": len(folder_backups),
                "backups": {
                    "files": file_backups,
                    "folders": folder_backups
                },
                "message": f"Found {len(backups)} total backup(s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list all backups"
            }
    
    @mcp.tool()
    async def backup_cancel(operation_id: str) -> Dict[str, Any]:
        """
        Cancel an active backup operation.
        
        Args:
            operation_id: ID of the operation to cancel
            
        Returns:
            Dictionary indicating whether the operation was cancelled
        """
        try:
            cancelled = backup_manager.cancel_operation(operation_id)
            if cancelled:
                return {
                    "success": True,
                    "operation_id": operation_id,
                    "message": f"Successfully cancelled operation {operation_id}"
                }
            else:
                return {
                    "success": False,
                    "operation_id": operation_id,
                    "message": f"Operation {operation_id} not found or already completed"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to cancel operation {operation_id}"
            }
