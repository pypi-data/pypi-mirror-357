from click.testing import CliRunner
from vaultix.cli.base import cli

def test_list_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['list', '--help'])
    assert result.exit_code == 0
    assert 'List all stored SSH connections' in result.output
