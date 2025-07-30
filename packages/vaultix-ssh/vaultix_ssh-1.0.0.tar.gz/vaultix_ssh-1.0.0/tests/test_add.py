from click.testing import CliRunner
from vaultix.cli.base import cli

def test_add_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['add', '--help'])
    assert result.exit_code == 0
    assert 'Add a new SSH connection' in result.output