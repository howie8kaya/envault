# Environment Switching

envault supports saving and restoring named **environment profiles** so you can
quickly flip between configurations (e.g. `dev`, `staging`, `prod`) without
manually editing secrets each time.

Profiles are stored in a sidecar file next to the vault:
`<vault-name>.profiles.json`. This file contains encrypted secret blobs in the
same format as the vault itself, so it is safe to commit alongside the vault.

---

## Commands

### Save the current vault state as a profile

```bash
envault profile save <profile-name> --vault .envault --passphrase ...
```

Captures every secret currently in the vault under the given name.

### List available profiles

```bash
envault profile list --vault .envault
```

Prints all saved profile names in alphabetical order.

### Switch to a profile

```bash
envault profile switch <profile-name> --vault .envault --passphrase ...
```

Replaces the vault's active secrets with those stored in the named profile.
The vault file is re-encrypted with the same passphrase.

### Delete a profile

```bash
envault profile delete <profile-name> --vault .envault
```

Removes the named profile from the sidecar file. The vault itself is unchanged.

---

## Example workflow

```bash
# Start on dev settings
envault profile save dev

# Switch to production secrets for a deploy
envault profile switch prod

# Come back to dev
envault profile switch dev
```

---

## Notes

- Switching a profile **overwrites** the vault's current secrets. Make sure to
  save your current state first if you want to return to it.
- The profiles sidecar file is **not** passphrase-protected on its own — the
  individual secret values remain encrypted via the vault's crypto layer.
- Profiles are identified by plain string names. Names are case-sensitive.
