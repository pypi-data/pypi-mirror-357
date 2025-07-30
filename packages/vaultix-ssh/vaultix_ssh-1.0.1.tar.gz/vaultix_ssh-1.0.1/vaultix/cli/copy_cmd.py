from .base import cli
from ..utils import print_info, print_error, print_success, print_warning
from ..config import ConfigManager
import subprocess
import click

config_manager = ConfigManager()

@cli.command()
@click.argument('name')
@click.argument('local_path')
@click.argument('remote_path')
@click.option('--download', '-d', is_flag=True, help="Download from remote to local")
@click.option('--recursive', '-r', is_flag=True, help="Copy directories recursively")
def copy(name, local_path, remote_path, download, recursive):
    """Copy files to/from remote server using SCP"""
    try:
        config = config_manager.load_config()
        if name not in config:
            print_error(f"Connection '{name}' not found")
            return

        conn = config[name]['connection']
        scp_cmd = ['scp']
        if recursive:
            scp_cmd.append('-r')
        if conn.get('key'):
            scp_cmd.extend(['-i', conn['key']])
        scp_cmd.extend(['-P', str(conn['port'])])

        if download:
            remote = f"{conn['user']}@{conn['host']}:{remote_path}"
            scp_cmd.extend([remote, local_path])
            print_info(f"Downloading {remote_path} → {local_path}")
        else:
            remote = f"{conn['user']}@{conn['host']}:{remote_path}"
            scp_cmd.extend([local_path, remote])
            print_info(f"Uploading {local_path} → {remote_path}")

        result = subprocess.run(scp_cmd)
        if result.returncode == 0:
            print_success("Transfer completed successfully")
        else:
            print_error("Transfer failed")
            sys.exit(result.returncode)

    except KeyboardInterrupt:
        print_warning("\nTransfer interrupted")
    except Exception as e:
        print_error(f"Transfer failed: {e}")