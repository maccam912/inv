# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Shipment Management Screen for viewing shipment information."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Label

from inv.db.operations import read_shipments


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
        # No need for the help text - it's in the footer now

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
