# vaultix/cli/base.py
import click
from ..constants import VERSION

@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True
)
@click.version_option(version=VERSION, prog_name="vaultix", message="%(prog)s v%(version)s")
@click.pass_context
def cli(ctx):
    """
    vaultix - Modern SSH Connection Manager

    Run `vaultix COMMAND --help` for more info on any command.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
