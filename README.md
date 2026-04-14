# envault

> A CLI tool for managing and encrypting `.env` files across multiple environments with team-sharing support.

---

## Installation

```bash
pip install envault
```

Or with pipx for isolated installs:

```bash
pipx install envault
```

---

## Usage

Initialize envault in your project:

```bash
envault init
```

Encrypt your `.env` file before committing or sharing:

```bash
envault encrypt --env production
```

Decrypt on another machine or teammate's environment:

```bash
envault decrypt --env production --key <your-secret-key>
```

Push an encrypted env to a shared vault:

```bash
envault push --env staging
```

Pull and decrypt a shared env:

```bash
envault pull --env staging
```

> **Tip:** Add `.env` to your `.gitignore` and commit only the encrypted `.env.vault` file safely.

---

## Supported Environments

- `development`
- `staging`
- `production`
- Custom named environments

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

This project is licensed under the [MIT License](LICENSE).