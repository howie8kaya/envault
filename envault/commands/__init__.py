"""envault command modules."""

from envault.commands.import_export import import_env, export_env
from envault.commands.rotate import rotate_key, list_rotation_candidates
from envault.commands.share import export_shared_bundle, import_shared_bundle
from envault.commands.audit import record_event, read_events, clear_log, format_events
from envault.commands.diff import diff_vault_vs_file, format_diff
from envault.commands.snapshot import create_snapshot, list_snapshots, restore_snapshot
from envault.commands.search import search_vault
from envault.commands.lint import lint_vault, format_lint_results
from envault.commands.template import render_template
from envault.commands.env_switch import save_profile, switch_profile, list_profiles
from envault.commands.copy import copy_secrets, list_copy_candidates
from envault.commands.rename import rename_secret, list_rename_candidates
from envault.commands.tags import add_tag, remove_tag, get_tags, list_tags
from envault.commands.history import record_history, get_history
from envault.commands.expire import set_expiry, get_expiry, list_expiring
from envault.commands.pin import pin_secret, unpin_secret, is_pinned, list_pinned
from envault.commands.watch import _sync_changes
from envault.commands.notes import set_note, get_note
from envault.commands.generate import generate_secret, list_charsets
from envault.commands.fmt import fmt_vault
from envault.commands.compare import compare_vaults
from envault.commands.lock import lock_vault, unlock_vault, get_session_passphrase, is_unlocked
from envault.commands.backup import create_backup, restore_backup, backup_info
from envault.commands.merge import merge_vaults, format_merge_results
from envault.commands.alias import set_alias, resolve_alias, list_aliases
from envault.commands.ttl import set_ttl, get_ttl, is_expired
from envault.commands.access import set_access, get_access, revoke_access, list_roles
from envault.commands.deps import add_dependency, remove_dependency, get_dependencies
from envault.commands.group import add_to_group, remove_from_group, get_group, list_groups
from envault.commands.group_export import export_group, group_summary
from envault.commands.schema import validate_vault
from envault.commands.schema_io import load_schema, save_schema
from envault.commands.webhook import register_webhook, unregister_webhook, list_webhooks
from envault.commands.webhook_audit import emit
from envault.commands.env_validate import validate_vault_types
from envault.commands.env_promote import promote_secrets, list_promote_candidates
from envault.commands.env_check import check_env, missing_keys
from envault.commands.env_mask import mask_secrets
from envault.commands.env_diff_apply import apply_diff_to_vault, apply_diff_to_file
from envault.commands.env_cast import cast_secret
from envault.commands.env_sort import sort_vault, is_sorted

__all__ = [
    "import_env", "export_env",
    "rotate_key", "list_rotation_candidates",
    "export_shared_bundle", "import_shared_bundle",
    "record_event", "read_events", "clear_log", "format_events",
    "diff_vault_vs_file", "format_diff",
    "create_snapshot", "list_snapshots", "restore_snapshot",
    "search_vault",
    "lint_vault", "format_lint_results",
    "render_template",
    "save_profile", "switch_profile", "list_profiles",
    "copy_secrets", "list_copy_candidates",
    "rename_secret", "list_rename_candidates",
    "add_tag", "remove_tag", "get_tags", "list_tags",
    "record_history", "get_history",
    "set_expiry", "get_expiry", "list_expiring",
    "pin_secret", "unpin_secret", "is_pinned", "list_pinned",
    "_sync_changes",
    "set_note", "get_note",
    "generate_secret", "list_charsets",
    "fmt_vault",
    "compare_vaults",
    "lock_vault", "unlock_vault", "get_session_passphrase", "is_unlocked",
    "create_backup", "restore_backup", "backup_info",
    "merge_vaults", "format_merge_results",
    "set_alias", "resolve_alias", "list_aliases",
    "set_ttl", "get_ttl", "is_expired",
    "set_access", "get_access", "revoke_access", "list_roles",
    "add_dependency", "remove_dependency", "get_dependencies",
    "add_to_group", "remove_from_group", "get_group", "list_groups",
    "export_group", "group_summary",
    "validate_vault",
    "load_schema", "save_schema",
    "register_webhook", "unregister_webhook", "list_webhooks",
    "emit",
    "validate_vault_types",
    "promote_secrets", "list_promote_candidates",
    "check_env", "missing_keys",
    "mask_secrets",
    "apply_diff_to_vault", "apply_diff_to_file",
    "cast_secret",
    "sort_vault", "is_sorted",
]
