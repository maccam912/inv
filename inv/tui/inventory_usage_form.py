# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Inventory Usage Form for recording inventory usage."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any, cast

from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Input, Label, Select, Static

from inv.db.operations import read_inventories, record_stock_usage
from inv.tui.forms import FormScreen, create_number_field, create_select_field

# Type for inventory selection
InventorySelection = tuple[str, str]


class InventoryUsageForm(FormScreen):
    """Form for recording inventory usage."""

    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the inventory usage form.

        Args:
            session_factory: A factory function to create database sessions
            *args: Additional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(session_factory, "Record Inventory Usage", *args, **kwargs)
        self.inventory_options: list[tuple[InventorySelection, str]] = []
        self.selected_inventory_id: InventorySelection | None = None
        self.current_quantity: int = 0

        # Load available inventory items
        with self.session_factory() as session:
            inventories = read_inventories(session)

            # Create options for dropdown with lot and site combinations
            self.inventory_options = [
                (
                    (inv.lot_number, inv.site_name),
                    f"{inv.lot_number} at {inv.site_name} ({inv.current_quantity} units)",
                )
                for inv in inventories
                if inv.current_quantity > 0  # Only include inventory with stock
            ]

            # Sort by lot number and site name
            self.inventory_options.sort(key=lambda x: (x[0][0], x[0][1]))

    def _compose_form(self) -> ComposeResult:
        """Create form fields for the inventory usage form."""
        with Vertical():
            if not self.inventory_options:
                yield Static("No inventory items available with stock.")
                # We need to mount the submit button but disable it
                submit_button = Button("Submit", variant="primary", id="submit")
                submit_button.disabled = True
                yield submit_button
            else:
                # Inventory selection dropdown
                yield from create_select_field(
                    "inventory_select",
                    "Select Inventory:",
                    options=self.inventory_options,
                )

                # Current quantity display (will be updated when inventory is selected)
                yield Label("Current Quantity:", classes="field-label")
                yield Static(
                    "Select an inventory item",
                    id="current_quantity",
                    classes="input-field",
                )

                # Quantity used input
                yield from create_number_field(
                    "quantity_used",
                    "Quantity Used:",
                    placeholder="Enter quantity used",
                )

    @property
    def _selected_inventory(self) -> InventorySelection | None:
        """Get the currently selected inventory."""
        select = self.query_one("#inventory_select", Select)
        value = select.value
        if value is None:
            return None
        return cast(InventorySelection, value)

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle inventory selection change."""
        if event.select.id == "inventory_select":
            value = event.value
            if value is None:
                self.selected_inventory_id = None
                return

            self.selected_inventory_id = cast(InventorySelection, value)

            # Update current quantity display
            if self.selected_inventory_id is not None:
                with self.session_factory() as session:
                    lot_number, site_name = self.selected_inventory_id
                    inventories = read_inventories(
                        session,
                        lot_number=lot_number,
                        site_name=site_name,
                    )
                    if inventories:
                        self.current_quantity = inventories[0].current_quantity
                        self.query_one("#current_quantity", Static).update(
                            f"{self.current_quantity} units"
                        )

    def validate_form(self) -> bool:
        """
        Validate the form inputs.

        Returns:
            True if validation passes, False otherwise
        """
        # Check if inventory is selected
        if self.selected_inventory_id is None:
            self.show_message("Please select an inventory item")
            return False

        # Get quantity used input
        quantity_input = self.query_one("#quantity_used", Input)

        # Validate quantity used
        try:
            quantity = int(quantity_input.value)
            if quantity <= 0:
                self.show_message("Quantity used must be positive")
                return False

            if quantity > self.current_quantity:
                self.show_message("Cannot use more than current quantity")
                return False
        except ValueError:
            self.show_message("Quantity used must be a number")
            return False

        return True

    def handle_submit(self) -> None:
        """Handle the submit button being pressed."""
        if not self.validate_form():
            return

        # Get form values
        if self.selected_inventory_id is None:
            self.show_message("No inventory selected.")
            return

        lot_number, site_name = self.selected_inventory_id
        quantity_input = self.query_one("#quantity_used", Input)
        quantity_used = int(quantity_input.value)

        try:
            with self.session_factory() as session:
                record_stock_usage(
                    session,
                    lot_number=lot_number,
                    site_name=site_name,
                    quantity_used=quantity_used,
                )
            self.dismiss(True)
        except ValueError as e:
            self.show_message(f"Error: {str(e)}")
            return  # Early return to prevent further processing
        except Exception as e:
            self.show_message(f"Error: {str(e)}")
            return  # Early return to prevent further processing
