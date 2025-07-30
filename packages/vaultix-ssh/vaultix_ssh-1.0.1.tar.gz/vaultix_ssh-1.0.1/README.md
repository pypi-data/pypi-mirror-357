# Vaultix - Modern SSH Connection Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

Vaultix is a modern SSH connection manager that makes it easy to organize, manage, and connect to your SSH servers. It features automatic SSH agent integration, secure storage, and a beautiful command-line interface.

---

## 🚀 Features

- 🔐 Secure connection storage with optional encryption
- 🔑 SSH Agent integration (auto-start, timeout, key reuse)
- 🎨 Rich CLI interface using `click` and `rich`
- 🔍 Fuzzy search & quick connect shortcuts
- 📦 JSON import/export support
- 💻 Execute remote commands or transfer files
- 🧪 Full test coverage via `pytest` and `pytest-cov`

---

## 🛠 Installation

### Via pip (Recommended)
```bash
pip install vaultix-ssh
```

### From Source

```bash
git clone https://github.com/Tusharmohanpuria/Vaultix-SSH
cd vaultix
pip install -e .
```

---

## ⚡ Quick Start

```bash
vaultix add myserver
vaultix myserver
```

---

## 🔧 Commands

| Command                           | Description                   |
| --------------------------------- | ----------------------------- |
| `vaultix list`                    | List all saved connections    |
| `vaultix add <name>`              | Add a new SSH connection      |
| `vaultix connect <name>`          | Connect via SSH               |
| `vaultix <name>`                  | Shortcut for `connect <name>` |
| `vaultix edit <name>`             | Edit existing connection      |
| `vaultix delete <name>`           | Delete a connection           |
| `vaultix rename <old> <new>`      | Rename a connection           |
| `vaultix show <name>`             | Display full details          |
| `vaultix search <query>`          | Find connections              |
| `vaultix copy <name> <src> <dst>` | Transfer files via SCP        |
| `vaultix exec <name> <cmd>`       | Execute remote shell command  |
| `vaultix export --json`           | Export connections to JSON    |
| `vaultix import --json`           | Import from JSON              |
| `vaultix agent`                   | Start and check SSH agent     |
| `vaultix config`                  | Show config paths and reset   |

---

## 📁 Examples

### Add with SSH options and test immediately

```bash
vaultix add prod-server
# Options: -J bastion.example.com -C
```

### Run remote commands

```bash
vaultix exec dev-server "uptime"
```

### Transfer files

```bash
vaultix copy prod-server ./file.txt /tmp/
vaultix copy prod-server /tmp/log.txt ./ --download
```

### Export and import configs

```bash
vaultix export --json --output vault-conns.json
vaultix import --json --input vault-conns.json
```

---

## 🧰 Troubleshooting

**SSH Agent Not Working?**

```bash
vaultix agent
eval $(ssh-agent -s)   # Linux
Start-Service ssh-agent  # Windows
```

**Check for broken entries**

```bash
vaultix check --connections
```

---

## 🤝 Contributing

Pull requests are welcome! All code is covered by automated tests (`pytest --cov`) and formatting enforced by `black`, `flake8`, and `mypy`.

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 👨‍💻 Author

Tushar Mohanpuria
[@Tusharmohanpuria](https://github.com/Tusharmohanpuria)