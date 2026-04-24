# env_chain — Vault Chain Resolution

Resolve and merge secrets from an ordered sequence of vaults into a single flat
dictionary. Later vaults in the chain take precedence over earlier ones,
allowing a layered override pattern (e.g. `base → staging → local`).

## API

### `resolve_chain(vault_paths, passphrases, keys=None) -> ChainResult`

Merge secrets from every vault in `vault_paths`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `vault_paths` | `List[Path]` | Ordered list of vault files |
| `passphrases` | `List[str]` | Matching passphrase for each vault |
| `keys` | `List[str] \| None` | Restrict to these keys; `None` = all |

Returns a `ChainResult` with:

- `merged` — final key→value dict after applying precedence rules
- `sources` — which vault each key was sourced from
- `chain` — ordered list of vault paths used

Raises `ChainError` if lengths mismatch, no vaults are supplied, or any vault
cannot be opened.

### `list_chain_candidates(vault_paths, passphrases) -> List[str]`

Return the de-duplicated union of all keys across every vault in the chain.
Useful for previewing what a `resolve_chain` call will touch.

## Example

```python
from pathlib import Path
from envault.commands.env_chain import resolve_chain

result = resolve_chain(
    vault_paths=[Path("base.vault"), Path("prod.vault")],
    passphrases=["base-pass", "prod-pass"],
)

for key, value in result.merged.items():
    print(f"{key}={value}  (from {result.sources[key]})")
```

## Precedence

Vaults are processed left-to-right. If the same key appears in multiple vaults
the **last** vault wins:

```
base.vault   SHARED_KEY=from_base
prod.vault   SHARED_KEY=from_prod   ← wins
```

## Errors

| Condition | Exception |
|-----------|-----------|
| `vault_paths` and `passphrases` differ in length | `ChainError` |
| Empty vault list | `ChainError` |
| Vault cannot be decrypted | `ChainError` |
