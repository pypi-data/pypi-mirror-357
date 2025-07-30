from .base import cli
from ..utils import print_error, print_success, print_warning, prompt_with_default
from ..config import ConfigManager
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from pathlib import Path
import click

console = Console()
config_manager = ConfigManager()

@cli.command()
@click.argument('name')
def edit(name):
    """Edit an existing SSH connection"""
    try:
        config = config_manager.load_config()
        if name not in config:
            print_error(f"Connection '{name}' not found")
            return

        console.print(Panel(f"Editing connection: [cyan]{name}[/cyan]"))

        conn = config[name]['connection']
        desc = config[name].get('description', '')

        config[name]['description'] = prompt_with_default("Description", desc)
        conn['host'] = prompt_with_default("Host", conn['host'])
        conn['user'] = prompt_with_default("Username", conn['user'])

        port = prompt_with_default("Port", str(conn['port']))
        try:
            conn['port'] = int(port)
        except ValueError:
            print_error("Port must be a number")
            return

        current_key = conn.get('key', '')
        if current_key:
            console.print(f"\nCurrent key: [yellow]{current_key}[/yellow]")
            if Confirm.ask("Change SSH key?", default=False):
                new_key = Prompt.ask("New SSH key path (empty to remove)", default="")
                conn['key'] = new_key if new_key else None
        else:
            if Confirm.ask("Add SSH key?", default=False):
                conn['key'] = Prompt.ask("SSH key path", default="~/.ssh/id_rsa")

        if conn.get('password'):
            if Confirm.ask("Update password?", default=False):
                conn['password'] = Prompt.ask("New password", password=True)
        elif not conn.get('key'):
            if Confirm.ask("Add password?", default=False):
                conn['password'] = Prompt.ask("Password", password=True)

        config_manager.save_config(config)
        print_success(f"Connection '{name}' updated successfully!")

    except KeyboardInterrupt:
        print_warning("\nOperation cancelled")
    except Exception as e:
        print_error(f"Failed to edit connection: {e}")