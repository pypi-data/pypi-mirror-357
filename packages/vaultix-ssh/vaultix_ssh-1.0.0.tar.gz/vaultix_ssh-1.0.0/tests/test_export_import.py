from click.testing import CliRunner
from vaultix.cli.base import cli
import tempfile
from pathlib import Path
from unittest.mock import patch

@patch("vaultix.config.ConfigManager.load_config")
@patch("vaultix.config.ConfigManager.save_config")
def test_import_export_json(mock_save, mock_load):
    mock_load.side_effect = [
        {
            "test": {
                "connection": {
                    "host": "localhost",
                    "user": "root",
                    "port": 22
                },
                "description": "export test"
            }
        },
        {}
    ]
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        json_path = Path(tmp) / "connections.json"
        result = runner.invoke(cli, ['export', '--json', '--output', str(json_path)])
        assert result.exit_code == 0
        assert json_path.exists()
        content = json_path.read_text()
        assert "localhost" in content
        result = runner.invoke(cli, ['import', '--json', '--input', str(json_path)])
        assert result.exit_code == 0
        assert mock_save.called