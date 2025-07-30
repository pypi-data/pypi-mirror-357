from click.testing import CliRunner
from vaultix.cli.base import cli
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

@patch("vaultix.config.ConfigManager.load_config")
@patch("vaultix.config.ConfigManager.save_config")
def test_add_cmd_prompts(mock_save, mock_load):
    mock_load.return_value = {}
    runner = CliRunner()
    inputs = "localhost\n22\nroot\n\n\nn\ndesc\n"
    result = runner.invoke(cli, ['add', 'test'], input=inputs)
    assert result.exit_code == 0
    assert mock_save.called

@patch("vaultix.config.ConfigManager.load_config")
@patch("vaultix.config.ConfigManager.save_config")
def test_edit_existing_connection(mock_save, mock_load):
    mock_load.return_value = {
        "test": {
            "connection": {
                "host": "localhost", "user": "root", "port": 22
            },
            "description": "old"
        }
    }
    runner = CliRunner()
    inputs = "\n\n\n\n\nnew description\nn\n"
    result = runner.invoke(cli, ['edit', 'test'], input=inputs)
    assert result.exit_code == 0
    assert "new description" in result.output or mock_save.called

@patch("vaultix.config.ConfigManager.load_config")
def test_delete_connection_prompt(mock_load):
    mock_load.return_value = {
        "test": {
            "connection": {"host": "127.0.0.1", "user": "root"},
            "description": "ok"
        }
    }
    runner = CliRunner()
    result = runner.invoke(cli, ['delete', 'test'], input='y\n')
    assert result.exit_code == 0

@patch("vaultix.config.ConfigManager.load_config")
def test_show_connection(mock_load):
    mock_load.return_value = {
        "test": {
            "connection": {
                "host": "127.0.0.1", "user": "root", "port": 22
            },
            "description": "ok"
        }
    }
    runner = CliRunner()
    result = runner.invoke(cli, ['show', 'test'])
    assert result.exit_code == 0
    assert "127.0.0.1" in result.output

@patch("vaultix.config.ConfigManager.load_config")
def test_check_connection_failure(mock_load):
    mock_load.return_value = {
        "test": {
            "connection": {"host": "nonexistent", "port": 22}
        }
    }
    runner = CliRunner()
    result = runner.invoke(cli, ['check', 'test'])
    assert result.exit_code in [1, 2]

@patch("vaultix.config.ConfigManager.load_config")
def test_list_command_output(mock_load):
    mock_load.return_value = {
        "conn": {
            "connection": {"host": "1.1.1.1"},
            "description": "desc"
        }
    }
    runner = CliRunner()
    result = runner.invoke(cli, ['list'])
    assert "conn" in result.output

@patch("vaultix.config.ConfigManager.load_config")
def test_search_matches(mock_load):
    mock_load.return_value = {
        "a": {"connection": {"host": "host1"}},
        "b": {"connection": {"host": "host2"}}
    }
    runner = CliRunner()
    result = runner.invoke(cli, ['search', 'host1'])
    assert "a" in result.output

@patch("vaultix.config.ConfigManager.load_config")
def test_rename_connection(mock_load):
    mock_load.return_value = {
        "old": {"connection": {"host": "localhost"}}
    }
    with patch("vaultix.config.ConfigManager.save_config") as mock_save:
        runner = CliRunner()
        result = runner.invoke(cli, ['rename', 'old', 'new'])
        assert result.exit_code == 0
        mock_save.assert_called()