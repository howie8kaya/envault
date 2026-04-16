"""envault command modules."""

from envault.commands.import_export import import_env, export_env
from envault.commands.rotate import rotate_key, list_rotation_candidates
from envault.commands.share import export_shared_bundle, import_shared_bundle
from envault.commands.audit import record_event, read_events, clear_log, format_events
from envault.commands.diff import diff_vault_vs_file, format_diff
from envault.commands.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
)
from envault.commands.search import search_vault
from envault.commands.lint import lint_vault, format_lint_results
from envault.commands.template import render_template
from envault.commands.env_switch import save_profile, switch_profile, list_profiles
from envault.commands.copy import copy_secrets, list_copy_candidates
from envault.commands.rename import rename_secret, list_rename_candidates
from envault.commands.tags import add_tag, remove_tag, list_tags, keys_with_tag
from envault.commands.history import record_history, get_history
from envault.commands.expire import set_expiry, get_expiry, list_expiring
from envault.commands.pin import pin_secret, unpin_secret, is_pinned, list_pinned
from envault.commands.watch import watch_env_file

__all__ = [
    "import_env", "export_env",
    "rotate_key", "list_rotation_candidates",
    "export_shared_bundle", "import_shared_bundle",
    "record_event", "read_events", "clear_log", "format_events",
    "diff_vault_vs_file", "format_diff",
    "create_snapshot", "list_snapshots", "restore_snapshot", "delete_snapshot",
    "search_vault",
    "lint_vault", "format_lint_results",
    "render_template",
    "save_profile", "switch_profile", "list_profiles",
    "copy_secrets", "list_copy_candidates",
    "rename_secret", "list_rename_candidates",
    "add_tag", "remove_tag", "list_tags", "keys_with_tag",
    "record_history", "get_history",
    "set_expiry", "get_expiry", "list_expiring",
    "pin_secret", "unpin_secret", "is_pinned", "list_pinned",
    "watch_env_file",
]
