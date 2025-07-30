from click.testing import CliRunner
from vaultix.cli.base import cli

def test_agent_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['agent', '--help'])
    assert result.exit_code == 0
    assert 'Manage SSH agent' in result.output
