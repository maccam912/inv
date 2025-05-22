# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Shipment Form for adding and editing shipments."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import date
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Select

from inv.db.models import Shipment
from inv.db.operations import (
    create_shipment,
    read_lots,
    read_shipment,
    read_sites,
    update_shipment,
)

# Import DatePicker from forms to ensure consistency
from inv.tui.forms import (
    DatePicker,
    FormScreen,
    create_date_field,
    create_number_field,
    create_select_field,
)


class ShipmentForm(FormScreen):
    """Form for adding or editing shipments."""

    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        shipment_id: int | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the shipment form.

        Args:
            session_factory: A factory function to create database sessions
            shipment_id: The shipment ID to edit (None for adding a new shipment)
            *args: Additional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        title = "Edit Shipment" if shipment_id else "Add New Shipment"
        super().__init__(session_factory, title, *args, **kwargs)
        self.shipment_id = shipment_id
        self.shipment: Shipment | None = None
        self.lot_options: list[tuple[str, str]] = []
        self.site_options: list[tuple[str, str]] = []

        # Load available lots and sites
        with self.session_factory() as session:
            # Load shipment if editing
            if shipment_id:
                self.shipment = read_shipment(session, shipment_id)

            # Get all lots for dropdown
            lots = read_lots(session)
            self.lot_options = [(lot.lot_number, lot.lot_number) for lot in lots]

            # Get all sites for dropdown
            sites = read_sites(session)
            self.site_options = [(site.site_name, site.site_name) for site in sites]

    def _compose_form(self) -> ComposeResult:
        """Create form fields for the shipment form."""
        with Vertical():
            if self.shipment:
                # Editing an existing shipment
                yield from create_select_field(
                    "lot_number",
                    "Lot Number:",
                    options=self.lot_options,
                    value=self.shipment.lot_number,
                )
                yield from create_select_field(
                    "site_name",
                    "Site Name:",
                    options=self.site_options,
                    value=self.shipment.site_name,
                )
                yield from create_date_field(
                    "shipment_date",
                    "Shipment Date:",
                    value=self.shipment.shipment_date,
                )
                yield from create_number_field(
                    "quantity_shipped",
                    "Quantity Shipped:",
                    value=self.shipment.quantity_shipped,
                    placeholder="Enter quantity shipped",
                )
                yield from create_date_field(
                    "anticipated_arrival_date",
                    "Anticipated Arrival Date:",
                    value=self.shipment.anticipated_arrival_date or date.today(),
                )
            else:
                # Adding a new shipment
                yield from create_select_field(
                    "lot_number", "Lot Number:", options=self.lot_options
                )
                yield from create_select_field(
                    "site_name", "Site Name:", options=self.site_options
                )
                yield from create_date_field("shipment_date", "Shipment Date:")
                yield from create_number_field(
                    "quantity_shipped",
                    "Quantity Shipped:",
                    placeholder="Enter quantity shipped",
                )
                yield from create_date_field(
                    "anticipated_arrival_date", "Anticipated Arrival Date:"
                )

    def validate_form(self) -> bool:
        """
        Validate the form inputs.

        Returns:
            True if validation passes, False otherwise
        """
        # Get form values
        lot_select = self.query_one("#lot_number", Select)
        site_select = self.query_one("#site_name", Select)
        quantity_input = self.query_one("#quantity_shipped", Input)

        # Validate lot number
        if lot_select.value is None:
            self.show_message("Lot number is required")
            return False

        # Validate site name
        if site_select.value is None:
            self.show_message("Site name is required")
            return False

        # Validate quantity shipped
        try:
            quantity = int(quantity_input.value)
            if quantity <= 0:
                self.show_message("Quantity shipped must be positive")
                return False
        except ValueError:
            self.show_message("Quantity shipped must be a number")
            return False

        return True

    def handle_submit(self) -> None:
        """Handle the submit button being pressed."""
        if not self.validate_form():
            return

        # Get form values
        lot_select = self.query_one("#lot_number", Select)
        site_select = self.query_one("#site_name", Select)
        shipment_date_picker = self.query_one("#shipment_date", DatePicker)
        quantity_input = self.query_one("#quantity_shipped", Input)
        arrival_date_picker = self.query_one("#anticipated_arrival_date", DatePicker)

        lot_number = str(lot_select.value)
        site_name = str(site_select.value)
        shipment_date = shipment_date_picker.value
        quantity_shipped = int(quantity_input.value)
        anticipated_arrival_date = arrival_date_picker.value

        try:
            with self.session_factory() as session:
                if self.shipment:
                    # Update existing shipment
                    if self.shipment_id is not None:
                        update_shipment(
                            session,
                            shipment_id=self.shipment_id,
                            lot_number=lot_number,
                            site_name=site_name,
                            shipment_date=shipment_date,
                            quantity_shipped=quantity_shipped,
                            anticipated_arrival_date=anticipated_arrival_date,
                        )
                else:
                    # Create new shipment
                    create_shipment(
                        session,
                        lot_number=lot_number,
                        site_name=site_name,
                        shipment_date=shipment_date,
                        quantity_shipped=quantity_shipped,
                        anticipated_arrival_date=anticipated_arrival_date,
                    )
            self.dismiss(True)
        except IntegrityError:
            self.show_message("Error: Invalid lot number or site name")
            return  # Early return to prevent further processing
        except Exception as e:
            self.show_message(f"Error: {str(e)}")
            return  # Early return to prevent further processing
