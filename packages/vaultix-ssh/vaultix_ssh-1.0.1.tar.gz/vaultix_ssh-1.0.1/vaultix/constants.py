import os
from pathlib import Path
from appdirs import user_config_dir

APP_NAME = "vaultix"
APP_AUTHOR = "vaultix"
VERSION = "1.0.0"

# Configuration paths
CONFIG_DIR = Path(user_config_dir(APP_NAME, APP_AUTHOR))
CONFIG_FILE = CONFIG_DIR / "connections.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

# SSH defaults
DEFAULT_SSH_PORT = 22
DEFAULT_SSH_USER = os.getenv("USER", "root")

# Agent settings
SSH_AGENT_TIMEOUT = 3600  # 1 hour
SSH_ADD_DEFAULT_OPTIONS = ["-t", str(SSH_AGENT_TIMEOUT)]

# Encryption
ENCRYPTION_KEY_FILE = CONFIG_DIR / ".vault_key"