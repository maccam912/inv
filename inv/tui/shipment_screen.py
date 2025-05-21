# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Shipment Management Screen for viewing shipment information."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

from sqlalchemy.orm import Session
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, DataTable, Label

from inv.db.operations import read_shipments, record_stock_arrival
from inv.tui.shipment_form import ShipmentForm


class ShipmentScreen(Container):
    """A screen for viewing and managing shipments."""

    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the ShipmentScreen.

        Args:
            session_factory: A context manager factory function to create database sessions
            *args: Additional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(*args, **kwargs)
        self.session_factory = session_factory
        self.shipments_table: DataTable | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the shipment screen."""
        yield Label("Shipment Management", classes="title")
        yield DataTable(id="shipments_table")

        with Horizontal(classes="button-container"):
            yield Button("Add Shipment", id="add_shipment", variant="primary")
            yield Button("Edit Selected", id="edit_shipment", variant="default")
            yield Button("Record Arrival", id="record_arrival", variant="success")

    def on_mount(self) -> None:
        """Set up the screen when it's mounted."""
        self.shipments_table = self.query_one("#shipments_table", DataTable)
        self.shipments_table.add_columns(
            "Shipment ID",
            "Lot Number",
            "Site Name",
            "Shipment Date",
            "Quantity Shipped",
            "Anticipated Arrival Date",
        )
        self.refresh_shipments()
        self.update_button_states()

    def refresh_shipments(self) -> None:
        """Refresh the shipments table with data from the database."""
        self.shipments_table = self.query_one("#shipments_table", DataTable)
        self.shipments_table.clear()

        with self.session_factory() as session:
            shipments = read_shipments(session)

            # Sort shipments by shipment date
            shipments.sort(key=lambda shipment: shipment.shipment_date)

            # Add rows for each shipment
            for shipment in shipments:
                anticipated_arrival = (
                    str(shipment.anticipated_arrival_date)
                    if shipment.anticipated_arrival_date
                    else "N/A"
                )
                self.shipments_table.add_row(
                    str(shipment.shipment_id),
                    shipment.lot_number,
                    shipment.site_name,
                    str(shipment.shipment_date),
                    str(shipment.quantity_shipped),
                    anticipated_arrival,
                    key=str(shipment.shipment_id),
                )

        self.update_button_states()

    def update_button_states(self) -> None:
        """Update the state of the edit and record arrival buttons based on the selected row."""
        edit_button = self.query_one("#edit_shipment", Button)
        record_arrival_button = self.query_one("#record_arrival", Button)

        has_selection = self.shipments_table.cursor_row is not None

        edit_button.disabled = not has_selection
        record_arrival_button.disabled = not has_selection

    @on(DataTable.RowSelected)
    def handle_row_selected(self) -> None:
        """Handle a row being selected in the table."""
        self.update_button_states()

    @on(DataTable.RowHighlighted)
    def handle_row_highlighted(self) -> None:
        """Handle a row being highlighted in the table."""
        self.update_button_states()

    @on(Button.Pressed, "#add_shipment")
    def handle_add_shipment(self) -> None:
        """Handle the add shipment button being pressed."""

        def handle_form_closed(result: bool) -> None:
            if result:
                self.refresh_shipments()

        form = ShipmentForm(self.session_factory)
        self.app.push_screen(form, handle_form_closed)

    @on(Button.Pressed, "#edit_shipment")
    def handle_edit_shipment(self) -> None:
        """Handle the edit shipment button being pressed."""
        shipment_id = int(
            self.shipments_table.get_row_at(self.shipments_table.cursor_row)[0]
        )

        def handle_form_closed(result: bool) -> None:
            if result:
                self.refresh_shipments()

        form = ShipmentForm(self.session_factory, shipment_id=shipment_id)
        self.app.push_screen(form, handle_form_closed)

    @on(Button.Pressed, "#record_arrival")
    def handle_record_arrival(self) -> None:
        """Handle the record arrival button being pressed."""
        shipment_id = int(
            self.shipments_table.get_row_at(self.shipments_table.cursor_row)[0]
        )

        with self.session_factory() as session:
            try:
                record_stock_arrival(session, shipment_id=shipment_id)
                self.app.notify(
                    "Shipment arrival recorded successfully", severity="information"
                )
            except Exception as e:
                self.app.notify(f"Error recording arrival: {str(e)}", severity="error")
