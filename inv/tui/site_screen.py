# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Site Management Screen for viewing site information."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Header, Label

from inv.db.operations import read_sites


class SiteScreen(Container):
    """A screen for viewing and managing sites."""

    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the SiteScreen.

        Args:
            session_factory: A context manager factory function to create database sessions
            *args: Additional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(*args, **kwargs)
        self.session_factory = session_factory
        self.sites_table: DataTable | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the site screen."""
        yield Header(show_clock=True)
        yield Label("Site Management", classes="title")
        yield DataTable(id="sites_table")
        yield Label("Press 'b' to go back to dashboard", classes="help")

    def on_mount(self) -> None:
        """Set up the screen when it's mounted."""
        self.sites_table = self.query_one("#sites_table", DataTable)
        self.sites_table.add_columns("Site Name", "Contact Information")
        self.refresh_sites()

    def refresh_sites(self) -> None:
        """Refresh the sites table with data from the database."""
        self.sites_table = self.query_one("#sites_table", DataTable)
        self.sites_table.clear()

        with self.session_factory() as session:
            sites = read_sites(session)

            # Sort sites by name
            sites.sort(key=lambda site: site.site_name)

            # Add rows for each site
            for site in sites:
                contact_info = site.contact_info or "N/A"
                self.sites_table.add_row(
                    site.site_name,
                    contact_info,
                    key=site.site_name,
                )
