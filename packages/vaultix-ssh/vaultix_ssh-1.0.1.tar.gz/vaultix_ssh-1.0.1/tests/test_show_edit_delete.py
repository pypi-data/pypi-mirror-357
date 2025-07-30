from click.testing import CliRunner
from vaultix.cli.base import cli
import json
import tempfile
from pathlib import Path

def test_edit_delete_show():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "connections.json"
        dummy_config = {
            "edit_test": {
                "connection": {
                    "host": "127.0.0.1",
                    "user": "root",
                    "port": 22,
                    "key": None,
                    "password": None,
                    "options": []
                },
                "description": "testing"
            }
        }
        config_path.write_text(json.dumps(dummy_config))
        result = runner.invoke(cli, ['show', 'edit_test'])
        assert result.exit_code == 0
        result = runner.invoke(cli, ['edit', 'edit_test'], input='test desc\n127.0.0.1\nroot\n22\nn\nn\n')
        assert result.exit_code == 0
        result = runner.invoke(cli, ['delete', 'edit_test'], input='y\n')
        assert result.exit_code == 0