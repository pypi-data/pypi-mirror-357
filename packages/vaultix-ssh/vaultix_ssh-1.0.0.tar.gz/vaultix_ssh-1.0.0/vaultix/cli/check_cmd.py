from .base import cli
from ..config import ConfigManager
from ..constants import SSH_AGENT_TIMEOUT
from ..ssh_agent import SSHAgent
from ..utils import print_info, print_success, print_error, print_warning
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import subprocess
import click

console = Console()
config_manager = ConfigManager()
ssh_agent = SSHAgent()

@cli.command()
@click.option('--connections', '-c', is_flag=True, help="Check all connections")
@click.option('--agent', '-a', is_flag=True, help="Check SSH agent")
@click.option('--keys', '-k', is_flag=True, help="Check SSH keys")
def check(connections, agent, keys):
    """Health check for vaultix setup"""
    console.print(Panel("vaultix Health Check", style="bold green"))
    all_good = True

    console.print("\n[bold]Configuration:[/bold]")
    try:
        config = config_manager.load_config()
        print_success(f"Configuration loaded successfully ({len(config)} connections)")
    except Exception as e:
        print_error(f"Configuration error: {e}")
        all_good = False

    if agent or not (connections or keys):
        console.print("\n[bold]SSH Agent:[/bold]")
        if ssh_agent.is_running():
            print_success("SSH agent is running")
            loaded_keys = ssh_agent.list_keys()
            if "no identities" in loaded_keys.lower():
                print_info("No keys loaded in agent")
            else:
                print_info("Keys loaded in agent")
        else:
            print_warning("SSH agent is not running")

    if keys or not (connections or agent):
        console.print("\n[bold]SSH Keys:[/bold]")
        try:
            config = config_manager.load_config()
            key_status = {}
            for name, conn_data in config.items():
                key_path = conn_data['connection'].get('key')
                if key_path:
                    key_file = Path(key_path).expanduser()
                    if key_file.exists():
                        key_status[name] = (key_path, True)
                    else:
                        key_status[name] = (key_path, False)
                        all_good = False
            if key_status:
                for name, (path, exists) in key_status.items():
                    if exists:
                        print_success(f"{name}: {path}")
                    else:
                        print_error(f"{name}: {path} (not found)")
            else:
                print_info("No SSH keys configured")
        except Exception as e:
            print_error(f"Error checking keys: {e}")
            all_good = False

    if connections:
        console.print("\n[bold]Connection Tests:[/bold]")
        try:
            config = config_manager.load_config()
            for name in config:
                conn = config[name]['connection']
                test_cmd = [
                    'ssh', '-o', 'ConnectTimeout=5',
                    '-o', 'BatchMode=yes',
                    '-p', str(conn['port']),
                    f"{conn['user']}@{conn['host']}",
                    'echo', 'OK'
                ]
                if conn.get('key'):
                    test_cmd.insert(1, '-i')
                    test_cmd.insert(2, conn['key'])
                result = subprocess.run(test_cmd, capture_output=True, text=True)
                if result.returncode == 0 and 'OK' in result.stdout:
                    print_success(f"{name}: Connection successful")
                else:
                    print_error(f"{name}: Connection failed")
                    all_good = False
        except Exception as e:
            print_error(f"Error testing connections: {e}")
            all_good = False

    console.print("\n" + "─" * 50)
    if all_good:
        print_success("All checks passed! ✨")
    else:
        print_warning("Some issues found. Please review above.")