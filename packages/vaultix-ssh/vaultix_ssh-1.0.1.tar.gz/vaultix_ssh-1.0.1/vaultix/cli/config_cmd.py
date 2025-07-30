from .base import cli
from ..utils import print_info, print_success
from ..constants import CONFIG_DIR, CONFIG_FILE, ENCRYPTION_KEY_FILE
from ..config import ConfigManager
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
import shutil
import click

console = Console()
config_manager = ConfigManager()

@cli.command(name='config')
@click.option('--show', is_flag=True, help="Show configuration paths")
@click.option('--reset', is_flag=True, help="Reset configuration")
def config_cmd(show, reset):
    """Manage vaultix configuration"""
    if show:
        console.print(Panel("vaultix Configuration", style="bold"))
        console.print(f"\nConfig directory: [cyan]{CONFIG_DIR}[/cyan]")
        console.print(f"Connections file: [cyan]{CONFIG_FILE}[/cyan]")
        console.print(f"Encryption key: [cyan]{ENCRYPTION_KEY_FILE}[/cyan]")

        if CONFIG_FILE.exists():
            config = config_manager.load_config()
            console.print(f"\nStored connections: [green]{len(config)}[/green]")
        else:
            console.print("\n[yellow]No configuration found[/yellow]")

    elif reset:
        if Confirm.ask("⚠️  This will delete ALL connections. Are you sure?", default=False):
            if Confirm.ask("Really sure? This cannot be undone!", default=False):
                if CONFIG_DIR.exists():
                    shutil.rmtree(CONFIG_DIR)
                    print_success("Configuration reset complete")
                else:
                    print_info("No configuration to reset")
        else:
            print_info("Reset cancelled")

    else:
        ctx = click.Context(config_cmd)
        ctx.invoke(config_cmd, show=True)