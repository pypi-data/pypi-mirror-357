from .base import cli
from ..utils import print_error, print_success, print_info
from ..config import ConfigManager
from rich.console import Console
from rich.prompt import Confirm
import click

console = Console()
config_manager = ConfigManager()

@cli.command()
@click.argument('name')
def delete(name):
    """Delete an SSH connection"""
    try:
        config = config_manager.load_config()
        if name not in config:
            print_error(f"Connection '{name}' not found")
            return

        console.print(f"\n[yellow]⚠️  About to delete connection: {name}[/yellow]")
        console.print(f"Host: {config[name]['connection']['host']}")

        if Confirm.ask("\nAre you sure?", default=False):
            del config[name]
            config_manager.save_config(config)
            print_success(f"Connection '{name}' deleted")
        else:
            print_info("Deletion cancelled")

    except Exception as e:
        print_error(f"Failed to delete connection: {e}")