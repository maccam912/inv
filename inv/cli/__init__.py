# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
import click

from inv.__about__ import __version__
from inv.tui.app import InventoryApp


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="inv")
@click.pass_context
def inv(ctx: click.Context):
    """Main entry point for the inv CLI."""
    if ctx.invoked_subcommand is None:
        app = InventoryApp()
        app.run()
