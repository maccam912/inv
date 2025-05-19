# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
import click

from ..__about__ import __version__


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="inv")
@click.pass_context
def inv(ctx: click.Context):
    if ctx.invoked_subcommand is None:
        # This is where the TUI app will be launched
        # from .tui.app import InventoryApp
        # app = InventoryApp()
        # app.run()
        click.echo("Launching TUI... (not implemented yet)")
    else:
        pass  # Handle subcommands if any are added later
