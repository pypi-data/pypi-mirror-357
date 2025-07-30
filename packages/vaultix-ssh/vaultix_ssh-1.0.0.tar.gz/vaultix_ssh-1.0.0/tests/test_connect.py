from click.testing import CliRunner
from vaultix.cli.base import cli

def test_connect_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['connect', '--help'])
    assert result.exit_code == 0
    assert 'Connect to an SSH server' in result.output