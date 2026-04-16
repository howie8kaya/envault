# Secret Tags

envault supports tagging secrets for grouping, filtering, and documentation purposes.
Tags are stored as metadata inside the vault and do not affect encryption.

## Commands

### Add a tag

```bash
envault tag add DB_URL database
envault tag add DB_URL infra
```

### Remove a tag

```bash
envault tag remove DB_URL infra
```

### List all tags

```bash
envault tag list
```

Example output:

```
DB_URL: database
API_KEY: external, infra
SECRET_TOKEN: (none)
```

### Filter secrets by tag

```bash
envault tag filter infra
```

Returns all secret keys that have the given tag applied.

## Use cases

- **Group by service**: tag secrets with `database`, `cache`, `auth`
- **Mark sensitivity**: tag secrets with `sensitive` or `public`
- **Environment hints**: tag with `prod-only` or `dev-only`
- **Export subsets**: combine with `export` to share only tagged secrets

## Notes

- Tags are stored under `_meta.tags` in the vault JSON (encrypted at rest).
- Adding the same tag twice is a no-op.
- Removing a tag that doesn't exist raises an error.
