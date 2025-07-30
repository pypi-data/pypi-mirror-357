from .base import cli
from ..utils import print_info, print_warning, print_error
from ..config import ConfigManager
from ..ssh_agent import SSHAgent
import subprocess
import click

config_manager = ConfigManager()
ssh_agent = SSHAgent()

@cli.command()
@click.argument('name')
@click.option('--no-agent', is_flag=True, help="Don't use SSH agent")
@click.option('-v', '--verbose', is_flag=True, help="Verbose SSH output")
def connect(name, no_agent, verbose):
    """Connect to an SSH server"""
    try:
        config = config_manager.load_config()
        if name not in config:
            print_error(f"Connection '{name}' not found. Use 'vaultix list' to see available connections.")
            return

        conn = config[name]['connection']

        if not no_agent and conn.get('key'):
            if not ssh_agent.is_running():
                ssh_agent.start()
            if ssh_agent.is_running():
                ssh_agent.add_key(conn['key'])

        ssh_cmd = ['ssh']
        if verbose:
            ssh_cmd.append('-v')
        if conn.get('key'):
            ssh_cmd.extend(['-i', conn['key']])
        if conn.get('options'):
            ssh_cmd.extend(conn['options'])
        ssh_cmd.extend(['-p', str(conn['port']), f"{conn['user']}@{conn['host']}"])

        print_info(f"Connecting to {conn['user']}@{conn['host']}:{conn['port']}...")
        if conn.get('password'):
            print_warning("Password authentication configured. You'll need to enter it manually.")

        subprocess.run(ssh_cmd)
    except KeyboardInterrupt:
        print_info("\n👋 Connection closed")
    except Exception as e:
        print_error(f"Connection failed: {e}")