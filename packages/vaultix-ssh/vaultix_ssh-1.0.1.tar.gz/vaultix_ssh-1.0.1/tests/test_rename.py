from click.testing import CliRunner
from vaultix.cli.base import cli
import json
import tempfile
from pathlib import Path

def test_rename():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "connections.json"
        dummy_config = {
            "oldname": {
                "connection": {
                    "host": "localhost",
                    "user": "user",
                    "port": 22,
                    "key": None,
                    "password": None,
                    "options": []
                },
                "description": "test"
            }
        }
        config_path.write_text(json.dumps(dummy_config))
        result = runner.invoke(cli, ['rename', 'oldname', 'newname'])
        assert result.exit_code == 0