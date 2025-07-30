from .base import cli
from ..utils import print_info, print_error, print_warning
from ..config import ConfigManager
from ..ssh_agent import SSHAgent
import subprocess
import sys
import click

config_manager = ConfigManager()
ssh_agent = SSHAgent()

@cli.command()
@click.argument('name')
@click.argument('command', nargs=-1, required=True)
@click.option('--no-agent', is_flag=True, help="Don't use SSH agent")
def exec(name, command, no_agent):
    """Execute a command on remote server"""
    try:
        config = config_manager.load_config()
        if name not in config:
            print_error(f"Connection '{name}' not found")
            return

        conn = config[name]['connection']

        if not no_agent and conn.get('key'):
            if not ssh_agent.is_running():
                ssh_agent.start()
            if ssh_agent.is_running():
                ssh_agent.add_key(conn['key'])

        ssh_cmd = ['ssh']
        if conn.get('key'):
            ssh_cmd.extend(['-i', conn['key']])
        ssh_cmd.extend(['-p', str(conn['port']), f"{conn['user']}@{conn['host']}", '--'])
        ssh_cmd.extend(command)

        print_info(f"Executing on {conn['host']}: {' '.join(command)}")
        result = subprocess.run(ssh_cmd)
        sys.exit(result.returncode)

    except KeyboardInterrupt:
        print_warning("\nCommand interrupted")
    except Exception as e:
        print_error(f"Execution failed: {e}")