# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Test the CLI module."""

import importlib


def test_cli_module():
    """Verify that the CLI module exports the inv function."""
    # Import the CLI module
    cli = importlib.import_module("inv.cli")

    # Check that the inv function is exported
    assert hasattr(cli, "inv"), "CLI module should export 'inv' function"

    # Check that it's a click command group
    import click

    assert isinstance(cli.inv, click.Group), "inv should be a click command group"
