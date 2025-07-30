from .base import cli
from ..utils import print_error, print_info, create_connection_table
from ..config import ConfigManager
from rich.console import Console
from rich.prompt import Prompt
import click

console = Console()
config_manager = ConfigManager()

@cli.command()
@click.argument('query', required=False)
def search(query):
    """Search connections by name, host, or description"""
    try:
        config = config_manager.load_config()
        if not config:
            print_info("No connections to search")
            return

        if not query:
            query = Prompt.ask("Search query")

        query = query.lower()
        matches = {}
        for name, conn_data in config.items():
            conn = conn_data['connection']
            desc = conn_data.get('description', '')
            if (query in name.lower() or query in conn['host'].lower() or
                query in conn['user'].lower() or query in desc.lower()):
                matches[name] = conn_data

        if matches:
            console.print(f"\nFound {len(matches)} matching connections:\n")
            table = create_connection_table(matches)
            console.print(table)
        else:
            print_info(f"No connections found matching '{query}'")
    except Exception as e:
        print_error(f"Search failed: {e}")