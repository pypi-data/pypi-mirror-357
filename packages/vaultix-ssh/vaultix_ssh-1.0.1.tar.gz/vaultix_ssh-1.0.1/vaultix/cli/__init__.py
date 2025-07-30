from .base import cli
from . import (
    list_cmd, add_cmd, show_cmd, connect_cmd, edit_cmd,
    delete_cmd, rename_cmd, exec_cmd, copy_cmd,
    agent_cmd, check_cmd, config_cmd, import_cmd,
    export_cmd, search_cmd
)

def main():
    cli()
