import click

from .commands.start import start
from .commands.stop import stop
from .commands.pause import pause
from .commands.resume import resume
from .commands.status import status
from .commands.edit import edit
from .commands.link import link
from .commands.report import report

@click.group()
def cli():
    """CLI-based timekeeping tool"""
    pass

# Register all commands
cli.add_command(start)
cli.add_command(stop)
cli.add_command(pause)
cli.add_command(resume)
cli.add_command(status)
cli.add_command(edit)
cli.add_command(link)
cli.add_command(report)

if __name__ == '__main__':
    cli()