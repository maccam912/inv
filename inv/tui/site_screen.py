# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Site Management Screen for viewing site information."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

from sqlalchemy.orm import Session
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, DataTable, Label

from inv.db.operations import read_sites
from inv.tui.site_form import SiteForm


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
        yield Label("Site Management", classes="title")
        yield DataTable(id="sites_table")

        with Horizontal(classes="button-container"):
            yield Button("Add Site", id="add_site", variant="primary")
            yield Button("Edit Selected", id="edit_site", variant="default")

    def on_mount(self) -> None:
        """Set up the screen when it's mounted."""
        self.sites_table = self.query_one("#sites_table", DataTable)
        self.sites_table.add_columns("Site Name", "Contact Information")
        self.refresh_sites()
        self.update_edit_button_state()

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

        self.update_edit_button_state()

    def update_edit_button_state(self) -> None:
        """Update the state of the edit button based on the selected row."""
        edit_button = self.query_one("#edit_site", Button)
        edit_button.disabled = self.sites_table.cursor_row is None

    @on(DataTable.RowSelected)
    def handle_row_selected(self) -> None:
        """Handle a row being selected in the table."""
        self.update_edit_button_state()

    @on(DataTable.RowHighlighted)
    def handle_row_highlighted(self) -> None:
        """Handle a row being highlighted in the table."""
        self.update_edit_button_state()

    @on(Button.Pressed, "#add_site")
    def handle_add_site(self) -> None:
        """Handle the add site button being pressed."""
        def handle_form_closed(result: bool) -> None:
            if result:
                self.refresh_sites()

        form = SiteForm(self.session_factory)
        self.app.push_screen(form, handle_form_closed)

    @on(Button.Pressed, "#edit_site")
    def handle_edit_site(self) -> None:
        """Handle the edit site button being pressed."""
        site_name = self.sites_table.get_row_at(self.sites_table.cursor_row)[0]

        def handle_form_closed(result: bool) -> None:
            if result:
                self.refresh_sites()

        form = SiteForm(self.session_factory, site_name=site_name)
        self.app.push_screen(form, handle_form_closed)
