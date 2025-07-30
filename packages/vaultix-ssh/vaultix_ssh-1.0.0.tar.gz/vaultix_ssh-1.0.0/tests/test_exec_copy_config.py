from click.testing import CliRunner
from vaultix.cli.base import cli
from unittest.mock import patch, MagicMock
import pytest

def test_exec_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['exec', '--help'])
    assert result.exit_code == 0
    assert 'Execute a command on remote server' in result.output

@patch("subprocess.run")
@patch("vaultix.config.ConfigManager.load_config")
def test_exec_command(mock_load_config, mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    mock_load_config.return_value = {
        "remote": {
            "connection": {
                "host": "localhost",
                "user": "user",
                "port": 22,
                "key": None,
                "password": None,
                "options": []
            },
            "description": "desc"
        }
    }
    runner = CliRunner()
    result = runner.invoke(cli, ['exec', 'remote', 'echo', 'hi'])
    assert result.exit_code == 0

@patch("subprocess.run")
@patch("vaultix.config.ConfigManager.load_config")
def test_copy_command(mock_load_config, mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    mock_load_config.return_value = {
        "remote": {
            "connection": {
                "host": "localhost",
                "user": "user",
                "port": 22,
                "key": None,
                "password": None,
                "options": []
            },
            "description": "desc"
        }
    }
    runner = CliRunner()
    result = runner.invoke(cli, ['copy', 'remote', 'src.txt', 'dest.txt'])
    assert result.exit_code == 0
    