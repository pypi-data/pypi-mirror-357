from click.testing import CliRunner
from vaultix.cli.base import cli

def test_check_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['check', '--help'])
    assert result.exit_code == 0
    assert 'Health check for vaultix setup' in result.output
    