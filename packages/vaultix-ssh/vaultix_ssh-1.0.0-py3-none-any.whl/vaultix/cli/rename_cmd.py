from .base import cli
from ..utils import print_error, print_success
from ..config import ConfigManager
import click

config_manager = ConfigManager()

@cli.command()
@click.argument('old_name')
@click.argument('new_name')
def rename(old_name, new_name):
    """Rename an SSH connection"""
    try:
        config = config_manager.load_config()
        if old_name not in config:
            print_error(f"Connection '{old_name}' not found")
            return
        if new_name in config:
            print_error(f"Connection '{new_name}' already exists")
            return

        config[new_name] = config[old_name]
        del config[old_name]
        config_manager.save_config(config)
        print_success(f"Renamed '{old_name}' → '{new_name}'")

    except Exception as e:
        print_error(f"Failed to rename connection: {e}")