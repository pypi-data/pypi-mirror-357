"""
Tests for BackupManager functionality.
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from mcp_auto_backup.core.backup import BackupManager
from mcp_auto_backup.core.storage import StorageManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage_manager(temp_dir):
    """Create a storage manager with temporary directory."""
    return StorageManager(temp_dir / "backups")


@pytest.fixture
def backup_manager(storage_manager):
    """Create a backup manager for testing."""
    return BackupManager(storage_manager)


@pytest.fixture
def sample_file(temp_dir):
    """Create a sample file for testing."""
    file_path = temp_dir / "test_file.txt"
    file_path.write_text("This is a test file content.")
    return file_path


@pytest.fixture
def sample_folder(temp_dir):
    """Create a sample folder structure for testing."""
    folder_path = temp_dir / "test_folder"
    folder_path.mkdir()
    
    (folder_path / "file1.txt").write_text("Content of file 1")
    (folder_path / "file2.py").write_text("print('Hello World')")
    
    subfolder = folder_path / "subfolder"
    subfolder.mkdir()
    (subfolder / "file3.md").write_text("# Markdown file")
    
    return folder_path


class TestBackupManager:
    """Test cases for BackupManager."""
    
    @pytest.mark.asyncio
    async def test_create_file_backup(self, backup_manager, sample_file):
        """Test creating a file backup."""
        result = await backup_manager.create_file_backup(
            sample_file, 
            "Test backup"
        )
        
        assert "backup_id" in result
        assert "timestamp" in result
        assert "file_size" in result
        assert "checksum" in result
        assert result["file_size"] > 0
    
    @pytest.mark.asyncio
    async def test_create_file_backup_nonexistent(self, backup_manager, temp_dir):
        """Test creating backup of non-existent file."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        
        with pytest.raises(FileNotFoundError):
            await backup_manager.create_file_backup(nonexistent_file)
    
    @pytest.mark.asyncio
    async def test_create_folder_backup(self, backup_manager, sample_folder):
        """Test creating a folder backup."""
        result = await backup_manager.create_folder_backup(
            sample_folder,
            context_description="Test folder backup"
        )
        
        assert "backup_id" in result
        assert "timestamp" in result
        assert "file_size" in result
        assert result["file_size"] > 0
    
    @pytest.mark.asyncio
    async def test_list_backups_for_path(self, backup_manager, sample_file):
        """Test listing backups for a specific path."""
        # Create a backup first
        await backup_manager.create_file_backup(sample_file, "First backup")
        await backup_manager.create_file_backup(sample_file, "Second backup")
        
        backups = await backup_manager.list_backups_for_path(sample_file)
        
        assert len(backups) == 2
        assert all("backup_id" in backup for backup in backups)
        assert all("timestamp" in backup for backup in backups)
    
    @pytest.mark.asyncio
    async def test_restore_file_backup(self, backup_manager, sample_file, temp_dir):
        """Test restoring a file backup."""
        # Create a backup
        backup_result = await backup_manager.create_file_backup(sample_file)
        backup_id = backup_result["backup_id"]
        
        # Modify the original file
        sample_file.write_text("Modified content")
        
        # Restore the backup
        restore_result = await backup_manager.restore_file_backup(backup_id)
        
        assert restore_result["backup_id"] == backup_id
        assert restore_result["checksum_verified"] is True
        
        # Check that content is restored
        restored_content = sample_file.read_text()
        assert restored_content == "This is a test file content."
    
    @pytest.mark.asyncio
    async def test_restore_nonexistent_backup(self, backup_manager):
        """Test restoring a non-existent backup."""
        with pytest.raises(ValueError, match="Backup not found"):
            await backup_manager.restore_file_backup("nonexistent-backup-id")
    
    @pytest.mark.asyncio
    async def test_list_all_backups(self, backup_manager, sample_file, sample_folder):
        """Test listing all backups in the system."""
        # Create some backups
        await backup_manager.create_file_backup(sample_file)
        await backup_manager.create_folder_backup(sample_folder)
        
        all_backups = await backup_manager.list_all_backups()
        
        assert len(all_backups) == 2
        backup_types = [backup["backup_type"] for backup in all_backups]
        assert "file" in backup_types
        assert "folder" in backup_types
    
    def test_cancel_operation(self, backup_manager):
        """Test cancelling an operation."""
        # Test cancelling non-existent operation
        result = backup_manager.cancel_operation("nonexistent-id")
        assert result is False
        
        # Test cancelling existing operation would require more complex setup
        # This is a basic test for the interface
