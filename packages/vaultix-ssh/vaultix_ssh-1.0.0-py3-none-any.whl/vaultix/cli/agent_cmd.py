from .base import cli
from ..ssh_agent import SSHAgent
from ..utils import print_success, print_error, print_info, print_warning
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()
ssh_agent = SSHAgent()

@cli.command()
def agent():
    """Manage SSH agent"""
    console.print(Panel("SSH Agent Status", style="bold"))
    if ssh_agent.is_running():
        print_success("SSH agent is running")
        console.print("\n[bold]Loaded keys:[/bold]")
        console.print(ssh_agent.list_keys())
        if Confirm.ask("\nRemove all keys from agent?", default=False):
            if ssh_agent.remove_all_keys():
                print_success("All keys removed from agent")
            else:
                print_error("Failed to remove keys")
    else:
        print_warning("SSH agent is not running")
        if Confirm.ask("\nStart SSH agent?", default=True):
            if ssh_agent.start():
                print_success("SSH agent started")
            else:
                print_error("Failed to start SSH agent")