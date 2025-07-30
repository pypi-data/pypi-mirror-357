import os
import sys
import json
import subprocess
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel

console = Console()

def print_success(message):
    """Print success message in green"""
    console.print(f"[green]✅ {message}[/green]")

def print_error(message):
    """Print error message in red"""
    console.print(f"[red]❌ {message}[/red]")

def print_warning(message):
    """Print warning message in yellow"""
    console.print(f"[yellow]⚠️  {message}[/yellow]")

def print_info(message):
    """Print info message in blue"""
    console.print(f"[blue]ℹ️  {message}[/blue]")

def prompt_with_default(prompt_text, default=""):
    """Prompt with optional default value"""
    if default:
        return Prompt.ask(prompt_text, default=default)
    return Prompt.ask(prompt_text)

def run_command(cmd, capture_output=True, check=True):
    """Run a shell command safely"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return e
    except FileNotFoundError:
        print_error(f"Command not found: {cmd[0]}")
        return None

def create_connection_table(connections):
    """Create a rich table for connections"""
    table = Table(title="SSH Connections", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Host", style="green")
    table.add_column("User", style="yellow")
    table.add_column("Port", style="blue")
    table.add_column("Description", style="white")
    
    for name, data in connections.items():
        conn = data.get('connection', {})
        table.add_row(
            name,
            conn.get('host', 'N/A'),
            conn.get('user', 'N/A'),
            str(conn.get('port', 22)),
            data.get('description', '')
        )
    
    return table