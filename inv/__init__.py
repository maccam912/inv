# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
import click

from inv.__about__ import __version__


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="inv")
@click.option(
    "--db-path",
    help="Path to the SQLite database file (can be on a network drive)",
    default=None,
    type=str,
)
@click.pass_context
def inv(ctx: click.Context, db_path: str | None):
    if ctx.invoked_subcommand is None:
        # Launch the TUI app
        from .tui.app import InventoryApp

        app = InventoryApp(db_path=db_path)
        app.run()
    else:
        pass  # Handle subcommands if any are added later
