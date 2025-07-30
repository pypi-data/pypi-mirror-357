from .base import cli
from ..utils import print_error, print_success
from ..config import ConfigManager
from pathlib import Path
from rich.prompt import Confirm
import json
import click

config_manager = ConfigManager()

@cli.command(name='import')
@click.argument('file')
@click.option('--merge', is_flag=True, help="Merge with existing connections")
def import_connections(file, merge):
    """Import connections from file"""
    try:
        import_path = Path(file)
        if not import_path.exists():
            print_error(f"File not found: {file}")
            return

        imported = json.loads(import_path.read_text())
        config = config_manager.load_config() if merge else {}
        count = 0
        for name, data in imported.items():
            if name in config:
                if Confirm.ask(f"Overwrite existing connection '{name}'?", default=False):
                    config[name] = data
                    count += 1
            else:
                config[name] = data
                count += 1

        config_manager.save_config(config)
        print_success(f"Imported {count} connections.")
    except Exception as e:
        print_error(f"Import failed: {e}")