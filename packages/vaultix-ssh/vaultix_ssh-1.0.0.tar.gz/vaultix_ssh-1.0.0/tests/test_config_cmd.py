from click.testing import CliRunner
from vaultix.cli.base import cli
from unittest.mock import patch
from vaultix.cli.config_cmd import CONFIG_DIR

def test_config_show():
    runner = CliRunner()
    with patch("vaultix.cli.config_cmd.ConfigManager.load_config") as mock_load:
        mock_load.return_value = {}
        result = runner.invoke(cli, ['config', '--show'])
        assert result.exit_code == 0

@patch("shutil.rmtree")
@patch("pathlib.Path.exists", return_value=True)
def test_config_reset(mock_exists, mock_rmtree):
    runner = CliRunner()
    result = runner.invoke(cli, ['config', '--reset'], input='y\ny\n')
    assert result.exit_code == 0
    mock_rmtree.assert_called_once_with(CONFIG_DIR)
