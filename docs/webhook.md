# Webhook Notifications

envault supports outbound webhook notifications when vault events occur. This lets you integrate with CI pipelines, Slack, or any HTTP endpoint.

## Registering a Webhook

```python
from envault.commands.webhook import register_webhook

info = register_webhook(vault_path, passphrase, "https://hooks.example.com/envault", events=["set", "delete"])
print(info)  # WebhookInfo(url='https://hooks.example.com/envault', events=['set', 'delete'])
```

## Supported Events

| Event | Description |
|-------|-------------|
| `set` | A secret was created or updated |
| `delete` | A secret was removed |
| `rotate` | The vault passphrase was rotated |
| `import` | Secrets were imported from a file |
| `export` | Secrets were exported |

## Listing Webhooks

```python
from envault.commands.webhook import list_webhooks

for hook in list_webhooks(vault_path, passphrase):
    print(hook.url, hook.events)
```

## Unregistering

```python
from envault.commands.webhook import unregister_webhook

unregister_webhook(vault_path, passphrase, "https://hooks.example.com/envault")
```

## Firing Notifications Manually

```python
from envault.commands.webhook import notify

results = notify(vault_path, passphrase, "set", {"key": "DATABASE_URL"})
for r in results:
    print(r["url"], r["status"])
```

## Error Handling

`WebhookError` is raised for invalid URLs, missing event lists, or network failures.

Webhook URLs must start with `http://` or `https://`.
