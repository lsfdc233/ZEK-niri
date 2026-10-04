"""State subpackage — snapshots and uninstall."""

from zekniri.state.backup import (
    backup_configs,
    delete_backup,
    get_all_backups,
    get_backup_base_dir,
    list_backups,
    rollback_configs,
)
from zekniri.state.uninstall import uninstall_zekniri

__all__ = [
    "backup_configs",
    "rollback_configs",
    "list_backups",
    "delete_backup",
    "get_all_backups",
    "get_backup_base_dir",
    "uninstall_zekniri",
]
