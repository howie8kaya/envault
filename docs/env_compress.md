# env_compress

Compress and decompress vault exports into compact base64 payloads. Useful for sharing secrets over size-limited channels (e.g., chat messages, QR codes).

## Functions

### `compress_vault(vault_path, passphrase, keys=None) -> CompressResult`

Decrypts secrets from the vault and produces a compressed, base64-encoded payload.

- `vault_path` — path to the `.vault` file
- `passphrase` — passphrase used to decrypt secrets
- `keys` — optional list of keys to include; defaults to all keys

Raises `CompressError` if any key is missing or decryption fails.

### `decompress_into_vault(payload, passphrase, vault_path, overwrite=False) -> list[str]`

Decodes a compressed payload and imports secrets into the target vault.

- `payload` — base64-encoded compressed string produced by `compress_vault`
- `passphrase` — passphrase used to re-encrypt secrets in the destination vault
- `vault_path` — destination vault path (created if it does not exist)
- `overwrite` — if `True`, existing keys are replaced; default is `False`

Returns the list of keys that were actually imported.

Raises `CompressError` if the payload is malformed.

## CompressResult

| Field | Type | Description |
|---|---|---|
| `key_count` | int | Number of secrets compressed |
| `original_size` | int | Uncompressed JSON size in bytes |
| `compressed_size` | int | Compressed size in bytes |
| `payload` | str | Base85-encoded compressed payload |

```python
result = compress_vault(Path("prod.vault"), "mypassphrase")
print(result)  # Compressed 5 keys: 312B -> 198B (36.5% reduction)

imported = decompress_into_vault(result.payload, "mypassphrase", Path("staging.vault"))
print(imported)  # ['DB_URL', 'API_KEY', ...]
```

## Notes

- Compression uses `zlib` at maximum level (9) and encodes with base85 for density.
- Secrets are decrypted before compression and re-encrypted after decompression — the payload itself is **not encrypted**. Treat it as sensitive.
