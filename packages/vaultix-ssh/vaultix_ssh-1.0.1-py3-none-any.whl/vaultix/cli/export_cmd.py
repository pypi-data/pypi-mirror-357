from .base import cli
from ..utils import print_error, print_success
from ..config import ConfigManager
from rich.console import Console
import json
from pathlib import Path
import click

console = Console()
config_manager = ConfigManager()

@cli.command()
@click.option('--json', 'format_json', is_flag=True, help="Export as JSON")
@click.option('--output', '-o', help="Output file (default: stdout)")
def export(format_json, output):
    """Export connections"""
    try:
        config = config_manager.load_config()
        if not config:
            console.print("[yellow]No connections to export[/yellow]")
            return

        if format_json:
            data = json.dumps(config, indent=2)
        else:
            lines = ["# vaultix SSH connections export\n"]
            for name, conn_data in config.items():
                conn = conn_data['connection']
                lines.append(f"\n[{name}]")
                lines.append(f"description = {conn_data.get('description', '')}")
                lines.append(f"host = {conn['host']}")
                lines.append(f"user = {conn['user']}")
                lines.append(f"port = {conn['port']}")
                if conn.get('key'):
                    lines.append(f"key = {conn['key']}")
                if conn.get('options'):
                    lines.append(f"options = {' '.join(conn['options'])}")
            data = '\n'.join(lines)

        if output:
            Path(output).write_text(data)
            print_success(f"Connections exported to {output}")
        else:
            console.print(data)
    except Exception as e:
        print_error(f"Export failed: {e}")