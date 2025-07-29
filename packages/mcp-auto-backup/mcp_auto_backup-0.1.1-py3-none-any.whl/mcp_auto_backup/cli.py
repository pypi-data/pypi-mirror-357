"""
Command Line Interface for MCP Auto Backup.

This module provides CLI commands for running the MCP server and managing backups.
"""

import click
import sys
from pathlib import Path
from typing import Optional

from .server import create_mcp_server
from .config.settings import get_settings, update_settings


@click.group()
@click.version_option(version="0.1.1", prog_name="mcp-auto-backup")
def cli():
    """MCP Auto Backup - A lightweight backup tool for AI Agents."""
    pass


@cli.command()
@click.option(
    "--backup-root",
    type=click.Path(path_type=Path),
    help="Root directory for backups (default: .mcp_backups)"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level"
)
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),
    help="Log file path (default: console only)"
)
@click.option(
    "--max-file-size",
    type=int,
    help="Maximum file size for backup in bytes"
)
@click.option(
    "--enable-encryption",
    is_flag=True,
    help="Enable backup encryption"
)
def serve(
    backup_root: Optional[Path],
    log_level: str,
    log_file: Optional[Path],
    max_file_size: Optional[int],
    enable_encryption: bool
):
    """Start the MCP Auto Backup server."""
    
    # Update settings with CLI options
    settings_updates = {"log_level": log_level}
    
    if backup_root:
        settings_updates["backup_root"] = backup_root
    if log_file:
        settings_updates["log_file"] = log_file
    if max_file_size:
        settings_updates["max_file_size"] = max_file_size
    if enable_encryption:
        settings_updates["enable_encryption"] = enable_encryption
    
    update_settings(**settings_updates)
    
    try:
        click.echo("Starting MCP Auto Backup Server...")
        mcp = create_mcp_server()
        mcp.run()
    except KeyboardInterrupt:
        click.echo("\nServer shutdown requested")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--backup-root",
    type=click.Path(path_type=Path),
    help="Root directory for backups (default: .mcp_backups)"
)
def info(backup_root: Optional[Path]):
    """Show backup system information."""
    
    if backup_root:
        update_settings(backup_root=backup_root)
    
    settings = get_settings()
    
    click.echo("MCP Auto Backup - System Information")
    click.echo("=" * 40)
    click.echo(f"Backup Root: {settings.backup_root}")
    click.echo(f"Encryption: {'Enabled' if settings.enable_encryption else 'Disabled'}")
    click.echo(f"Max File Size: {settings.max_file_size / (1024*1024):.1f} MB")
    click.echo(f"Auto Cleanup: {settings.auto_cleanup_days} days")
    click.echo(f"Safety Backups: {'Enabled' if settings.create_safety_backups else 'Disabled'}")
    click.echo(f"Checksum Verification: {'Enabled' if settings.verify_checksums else 'Disabled'}")
    
    # Check if backup directory exists and show stats
    if settings.backup_root.exists():
        files_dir = settings.backup_root / "files"
        folders_dir = settings.backup_root / "folders"
        
        file_backups = len(list(files_dir.glob("*"))) if files_dir.exists() else 0
        folder_backups = len(list(folders_dir.glob("*"))) if folders_dir.exists() else 0
        
        click.echo(f"\nBackup Statistics:")
        click.echo(f"File Backups: {file_backups}")
        click.echo(f"Folder Backups: {folder_backups}")
        click.echo(f"Total: {file_backups + folder_backups}")
    else:
        click.echo(f"\nBackup directory does not exist yet.")


@cli.command()
@click.option(
    "--backup-root",
    type=click.Path(path_type=Path),
    help="Root directory for backups (default: .mcp_backups)"
)
@click.confirmation_option(
    prompt="Are you sure you want to initialize the backup system?"
)
def init(backup_root: Optional[Path]):
    """Initialize the backup system."""
    
    if backup_root:
        update_settings(backup_root=backup_root)
    
    settings = get_settings()
    
    try:
        # Create backup directories
        settings.backup_root.mkdir(parents=True, exist_ok=True)
        (settings.backup_root / "files").mkdir(exist_ok=True)
        (settings.backup_root / "folders").mkdir(exist_ok=True)
        
        # Create initial metadata file
        metadata_file = settings.backup_root / "metadata.json"
        if not metadata_file.exists():
            import json
            from datetime import datetime
            
            initial_metadata = {
                "backups": {},
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(initial_metadata, f, indent=2)
        
        click.echo(f"✅ Backup system initialized at: {settings.backup_root}")
        click.echo("You can now start the MCP server with: mcp-auto-backup serve")
        
    except Exception as e:
        click.echo(f"❌ Failed to initialize backup system: {e}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    click.echo("MCP Auto Backup v0.1.1")
    click.echo("A lightweight backup tool for AI Agents")
    click.echo("Built with Model Context Protocol (MCP)")


def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
