from .base import cli
from ..utils import print_info, print_error, create_connection_table
from ..config import ConfigManager
from rich.console import Console

console = Console()
config_manager = ConfigManager()

@cli.command()
def list():
    """List all stored SSH connections"""
    try:
        config = config_manager.load_config()
        if not config:
            print_info("No connections found. Use 'vaultix add' to create one.")
            return
        table = create_connection_table(config)
        console.print(table)
    except Exception as e:
        print_error(f"Failed to load connections: {e}")