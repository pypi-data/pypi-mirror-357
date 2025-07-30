from click.testing import CliRunner
from vaultix.cli.base import cli

def test_search_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['search', '--help'])
    assert result.exit_code == 0
    assert 'Search connections by name' in result.output
    