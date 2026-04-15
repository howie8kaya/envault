# Template Rendering

envault can render template files by substituting `{{KEY}}` placeholders with
decrypted secrets from a vault file. This is useful for generating config files,
docker-compose overrides, CI environment scripts, and more.

## Placeholder syntax

Use double curly braces around any vault key name:

```
DATABASE_URL=postgres://{{DB_USER}}:{{DB_PASS}}@{{DB_HOST}}:{{DB_PORT}}/{{DB_NAME}}
API_KEY={{API_KEY}}
```

Whitespace inside the braces is ignored, so `{{ DB_HOST }}` and `{{DB_HOST}}`
are equivalent.

## Python API

### `render_template(template_text, vault_path, passphrase, *, strict=False)`

Render a template string in memory.

```python
from pathlib import Path
from envault.commands.template import render_template

result = render_template(
    "host={{DB_HOST}} port={{DB_PORT}}",
    vault_path=Path(".envault"),
    passphrase="my-passphrase",
)
print(result.output)       # host=localhost port=5432
print(result.substituted)  # ['DB_HOST', 'DB_PORT']
print(result.missing)      # []
```

### `render_template_file(template_path, vault_path, passphrase, output_path=None, *, strict=False)`

Read a template from disk, render it, and optionally write the result.

```python
from pathlib import Path
from envault.commands.template import render_template_file

render_template_file(
    template_path=Path("config.tmpl"),
    vault_path=Path(".envault"),
    passphrase="my-passphrase",
    output_path=Path(".env"),
)
```

## Strict mode

By default, unresolved placeholders are left unchanged in the output and
recorded in `result.missing`. Pass `strict=True` to raise a `TemplateError`
instead:

```python
render_template(tmpl, vault_path, passphrase, strict=True)
# raises TemplateError: Template key 'MISSING_KEY' not found in vault
```

## Return value — `RenderResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `output` | `str` | Rendered text |
| `substituted` | `list[str]` | Keys successfully replaced |
| `missing` | `list[str]` | Keys not found in vault |
| `has_missing` | `bool` | Convenience property |
