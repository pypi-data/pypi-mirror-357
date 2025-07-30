from .base import cli
from ..utils import print_error, print_success, print_warning, prompt_with_default
from ..config import ConfigManager
from ..constants import DEFAULT_SSH_PORT, DEFAULT_SSH_USER
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from pathlib import Path
import click

console = Console()
config_manager = ConfigManager()

@cli.command()
@click.argument('name')
def add(name):
    """Add a new SSH connection"""
    try:
        config = config_manager.load_config()

        if name in config:
            print_error(f"Connection '{name}' already exists")
            return

        console.print(Panel(f"Adding new connection: [cyan]{name}[/cyan]"))

        host = Prompt.ask("Host (IP or domain)")
        if not host:
            print_error("Host is required")
            return

        user = prompt_with_default("Username", DEFAULT_SSH_USER)
        port = prompt_with_default("Port", str(DEFAULT_SSH_PORT))
        try:
            port = int(port)
        except ValueError:
            print_error("Port must be a number")
            return

        description = Prompt.ask("Description (optional)", default="")

        use_key = Confirm.ask("Use SSH key authentication?", default=True)
        key_path = None
        password = None

        if use_key:
            key_path = Prompt.ask("SSH key path", default="~/.ssh/id_rsa")
            key_path = str(Path(key_path).expanduser())
            if not Path(key_path).exists():
                print_warning(f"Key file not found: {key_path}")
                if not Confirm.ask("Continue anyway?", default=False):
                    return
        else:
            use_password = Confirm.ask("Store password?", default=False)
            if use_password:
                password = Prompt.ask("Password", password=True)

        extra_options = []
        if Confirm.ask("Add extra SSH options?", default=False):
            console.print("\nCommon options: -X (X11), -A (agent forwarding), -C (compression)")
            options = Prompt.ask("Enter SSH options (space-separated)", default="")
            if options:
                extra_options = options.split()

        connection_data = {
            "connection": {
                "host": host,
                "user": user,
                "port": port,
                "key": key_path,
                "password": password,
                "options": extra_options
            },
            "description": description
        }

        config[name] = connection_data
        config_manager.save_config(config)
        print_success(f"Connection '{name}' added successfully!")

    except KeyboardInterrupt:
        print_warning("\nOperation cancelled")
    except Exception as e:
        print_error(f"Failed to add connection: {e}")
