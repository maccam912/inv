# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Inventory Management Screen for viewing inventory levels."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

from sqlalchemy.orm import Session
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, DataTable, Label

from inv.db.operations import read_inventories
from inv.tui.inventory_usage_form import InventoryUsageForm


class InventoryScreen(Container):
    """A screen for viewing current inventory levels at each site."""

    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the InventoryScreen.

        Args:
            session_factory: A context manager factory function to create database sessions
            *args: Additional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(*args, **kwargs)
        self.session_factory = session_factory
        self.inventory_table: DataTable | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the inventory screen."""
        yield Label("Inventory Tracking", classes="title")
        yield DataTable(id="inventory_table")

        with Horizontal(classes="button-container"):
            yield Button("Record Usage", id="record_usage", variant="primary")

    def on_mount(self) -> None:
        """Set up the screen when it's mounted."""
        self.inventory_table = self.query_one("#inventory_table", DataTable)
        self.inventory_table.add_columns(
            "Lot Number",
            "Site Name",
            "Current Quantity",
            "Last Updated Date",
        )
        self.refresh_inventory()

    def refresh_inventory(self) -> None:
        """Refresh the inventory table with data from the database."""
        self.inventory_table = self.query_one("#inventory_table", DataTable)
        self.inventory_table.clear()

        with self.session_factory() as session:
            inventories = read_inventories(session)

            # Sort inventories by site name, then by lot number
            inventories.sort(
                key=lambda inventory: (inventory.site_name, inventory.lot_number)
            )

            # Add rows for each inventory record
            for inventory in inventories:
                self.inventory_table.add_row(
                    inventory.lot_number,
                    inventory.site_name,
                    str(inventory.current_quantity),
                    str(inventory.last_updated_date),
                    key=f"{inventory.lot_number}-{inventory.site_name}",
                )

    @on(Button.Pressed, "#record_usage")
    def handle_record_usage(self) -> None:
        """Handle the record usage button being pressed."""
        def handle_form_closed(result: bool) -> None:
            if result:
                self.refresh_inventory()

        form = InventoryUsageForm(self.session_factory)
        self.app.push_screen(form, handle_form_closed)
