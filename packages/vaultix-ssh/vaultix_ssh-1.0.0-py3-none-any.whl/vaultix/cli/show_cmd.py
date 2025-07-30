from .base import cli
from ..utils import print_error
from ..config import ConfigManager
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from pathlib import Path
import click

console = Console()
config_manager = ConfigManager()

@cli.command()
@click.argument('name')
def show(name):
    """Show detailed connection information"""
    try:
        config = config_manager.load_config()
        if name not in config:
            print_error(f"Connection '{name}' not found")
            return

        conn_data = config[name]
        conn = conn_data['connection']

        tree = Tree(f"[bold cyan]{name}[/bold cyan]")
        tree.add(f"Description: {conn_data.get('description', 'N/A')}")

        conn_tree = tree.add("Connection Details")
        conn_tree.add(f"Host: [green]{conn['host']}[/green]")
        conn_tree.add(f"User: [yellow]{conn['user']}[/yellow]")
        conn_tree.add(f"Port: [blue]{conn['port']}[/blue]")

        auth_tree = tree.add("Authentication")
        if conn.get('key'):
            auth_tree.add(f"SSH Key: [magenta]{conn['key']}[/magenta]")
            key_path = Path(conn['key']).expanduser()
            if key_path.exists():
                auth_tree.add("[green]\u2713 Key file exists[/green]")
            else:
                auth_tree.add("[red]\u2717 Key file not found[/red]")

        if conn.get('password'):
            auth_tree.add("[yellow]Password authentication configured[/yellow]")

        if conn.get('options'):
            opts_tree = tree.add("SSH Options")
            for opt in conn['options']:
                opts_tree.add(opt)

        console.print(Panel(tree, title=f"Connection: {name}"))

        ssh_cmd = f"ssh"
        if conn.get('key'):
            ssh_cmd += f" -i {conn['key']}"
        if conn.get('options'):
            ssh_cmd += f" {' '.join(conn['options'])}"
        ssh_cmd += f" -p {conn['port']} {conn['user']}@{conn['host']}"

        console.print(f"\n[dim]SSH Command:[/dim] [cyan]{ssh_cmd}[/cyan]")

    except Exception as e:
        print_error(f"Failed to show connection: {e}")
