# 🔐 Vaultix-SSH

A cross-platform CLI tool for managing, connecting, and organizing SSH configurations with ease.  
Vaultix-SSH helps you handle SSH connections using structured config files, prompts, and commands.

---

## 📦 Features

- Add, edit, delete SSH connections with prompts or arguments.
- Easily connect to configured hosts.
- Export/import connections in JSON/YAML.
- Execute remote commands or copy files.
- Manage your SSH agent keys.
- Rich CLI experience using `Click` and `Rich`.

---

## 🚀 Installation

### 💻 Linux / macOS

```bash
./scripts/install.sh
```

### 🪟 Windows (PowerShell)

```powershell
.\scripts\install.ps1
```

To uninstall:

```bash
./scripts/uninstall.sh
```

---

## 🧭 Usage

### Basic Commands

```bash
vaultix add <name>       # Add a new SSH connection
vaultix list             # List saved connections
vaultix connect <name>   # Connect via SSH
vaultix delete <name>    # Delete a connection
vaultix edit <name>      # Edit a connection
vaultix export --json    # Export connections to JSON
vaultix import --json    # Import connections from JSON
vaultix agent            # Manage ssh-agent (add/remove keys)
vaultix exec <name>      # Run a command remotely
```

Run `vaultix --help` to see all available options.

---

## 🔧 Configuration

Vaultix stores SSH connection configs in a local JSON file under:

* **Linux/macOS:** `~/.config/vaultix/config.json`
* **Windows:** `%USERPROFILE%\.config\vaultix\config.json`

See [`examples/config-examples.json`](examples/config-examples.json) for the format.

---

## 🧪 Testing

Run all tests with coverage:

```bash
pytest --cov --cov-config=.coveragerc
```

---

## 📄 Documentation

* [Installation Guide](docs/installation.md)
* [Usage Guide](docs/usage.md)
* [Troubleshooting](docs/troubleshooting.md)
* [Configuration Examples](examples/config-examples.json)
* [Contributing](docs/CONTRIBUTING.md)

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
