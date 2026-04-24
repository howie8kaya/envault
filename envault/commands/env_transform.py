"""env_transform.py — Apply transformation functions to vault secret values.

Supported transforms: upper, lower, strip, reverse, base64_encode,
base64_decode, url_encode, url_decode, sha256, md5.
"""

from __future__ import annotations

import base64
import hashlib
import urllib.parse
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from envault.vault import VaultError, load_vault, save_vault

# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class TransformError(Exception):
    """Raised when a transformation cannot be applied."""


# ---------------------------------------------------------------------------
# Available transforms
# ---------------------------------------------------------------------------

_TRANSFORMS: Dict[str, Callable[[str], str]] = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "reverse": lambda v: v[::-1],
    "base64_encode": lambda v: base64.b64encode(v.encode()).decode(),
    "base64_decode": lambda v: base64.b64decode(v.encode()).decode(),
    "url_encode": urllib.parse.quote,
    "url_decode": urllib.parse.unquote,
    "sha256": lambda v: hashlib.sha256(v.encode()).hexdigest(),
    "md5": lambda v: hashlib.md5(v.encode()).hexdigest(),  # noqa: S324
}


def list_transforms() -> List[str]:
    """Return the names of all available transform functions."""
    return sorted(_TRANSFORMS.keys())


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class TransformResult:
    key: str
    transform: str
    old_value: str
    new_value: str
    changed: bool

    def __str__(self) -> str:  # noqa: D105
        if self.changed:
            return f"{self.key}: [{self.transform}] '{self.old_value}' -> '{self.new_value}'"
        return f"{self.key}: [{self.transform}] no change"


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def transform_secret(
    vault_path: str,
    passphrase: str,
    key: str,
    transform: str,
    *,
    dry_run: bool = False,
) -> TransformResult:
    """Apply *transform* to the value stored under *key* in the vault.

    Parameters
    ----------
    vault_path:  Path to the vault file.
    passphrase:  Vault passphrase used for decryption / re-encryption.
    key:         Secret key whose value will be transformed.
    transform:   Name of the transform to apply (see ``list_transforms()``).
    dry_run:     If *True*, compute the result but do not persist the change.

    Returns
    -------
    TransformResult with the before/after values.

    Raises
    ------
    TransformError  If the transform name is unknown, the key is missing, or
                    the transform function itself raises (e.g. invalid base64).
    """
    if transform not in _TRANSFORMS:
        raise TransformError(
            f"Unknown transform '{transform}'. "
            f"Available: {', '.join(list_transforms())}"
        )

    vault = load_vault(vault_path, passphrase)
    secrets: Dict[str, str] = vault.get("secrets", {})

    if key not in secrets:
        raise TransformError(f"Key '{key}' not found in vault.")

    old_value = secrets[key]
    fn = _TRANSFORMS[transform]

    try:
        new_value = fn(old_value)
    except Exception as exc:
        raise TransformError(
            f"Transform '{transform}' failed on key '{key}': {exc}"
        ) from exc

    changed = new_value != old_value

    if changed and not dry_run:
        secrets[key] = new_value
        vault["secrets"] = secrets
        save_vault(vault_path, passphrase, vault)

    return TransformResult(
        key=key,
        transform=transform,
        old_value=old_value,
        new_value=new_value,
        changed=changed,
    )


def transform_all(
    vault_path: str,
    passphrase: str,
    transform: str,
    *,
    keys: Optional[List[str]] = None,
    dry_run: bool = False,
) -> List[TransformResult]:
    """Apply *transform* to every key in *keys* (or all keys if omitted).

    Returns a list of :class:`TransformResult` objects, one per processed key.
    """
    if transform not in _TRANSFORMS:
        raise TransformError(
            f"Unknown transform '{transform}'. "
            f"Available: {', '.join(list_transforms())}"
        )

    vault = load_vault(vault_path, passphrase)
    secrets: Dict[str, str] = vault.get("secrets", {})
    target_keys = keys if keys is not None else list(secrets.keys())

    missing = [k for k in target_keys if k not in secrets]
    if missing:
        raise TransformError(f"Keys not found in vault: {', '.join(missing)}")

    fn = _TRANSFORMS[transform]
    results: List[TransformResult] = []

    for k in target_keys:
        old_value = secrets[k]
        try:
            new_value = fn(old_value)
        except Exception as exc:
            raise TransformError(
                f"Transform '{transform}' failed on key '{k}': {exc}"
            ) from exc

        changed = new_value != old_value
        if changed and not dry_run:
            secrets[k] = new_value

        results.append(
            TransformResult(
                key=k,
                transform=transform,
                old_value=old_value,
                new_value=new_value,
                changed=changed,
            )
        )

    if not dry_run:
        vault["secrets"] = secrets
        save_vault(vault_path, passphrase, vault)

    return results
