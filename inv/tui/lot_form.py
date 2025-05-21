# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Lot Form for adding and editing lots."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DatePicker, Input

from inv.db.models import Lot
from inv.db.operations import create_lot, read_lot, update_lot
from inv.tui.forms import (
    FormScreen,
    create_date_field,
    create_number_field,
    create_text_field,
)


class LotForm(FormScreen):
    """Form for adding or editing lots."""

    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        lot_number: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the lot form.

        Args:
            session_factory: A factory function to create database sessions
            lot_number: The lot number to edit (None for adding a new lot)
            *args: Additional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        title = "Edit Lot" if lot_number else "Add New Lot"
        super().__init__(session_factory, title, *args, **kwargs)
        self.lot_number = lot_number
        self.lot: Lot | None = None

        if lot_number:
            with self.session_factory() as session:
                self.lot = read_lot(session, lot_number)

    def _compose_form(self) -> ComposeResult:
        """Create form fields for the lot form."""
        with Vertical():
            if self.lot:
                # Editing an existing lot
                yield from create_text_field(
                    "lot_number",
                    "Lot Number:",
                    value=self.lot.lot_number,
                    placeholder="Enter lot number",
                )
                # Make the lot number field read-only in edit mode
                lot_number_input = self.query_one("#lot_number", Input)
                lot_number_input.disabled = True

                yield from create_date_field(
                    "expiration_date",
                    "Expiration Date:",
                    value=self.lot.expiration_date,
                )
                yield from create_number_field(
                    "initial_quantity",
                    "Initial Quantity:",
                    value=self.lot.initial_quantity,
                    placeholder="Enter initial quantity",
                )
            else:
                # Adding a new lot
                yield from create_text_field(
                    "lot_number",
                    "Lot Number:",
                    placeholder="Enter lot number",
                )
                yield from create_date_field("expiration_date", "Expiration Date:")
                yield from create_number_field(
                    "initial_quantity",
                    "Initial Quantity:",
                    placeholder="Enter initial quantity",
                )

    def validate_form(self) -> bool:
        """
        Validate the form inputs.

        Returns:
            True if validation passes, False otherwise
        """
        # Get form values
        lot_number_input = self.query_one("#lot_number", Input)
        expiration_date_picker = self.query_one("#expiration_date", DatePicker)
        initial_quantity_input = self.query_one("#initial_quantity", Input)

        # Validate lot number
        if not lot_number_input.value:
            self.show_message("Lot number is required")
            return False

        # Validate expiration date
        if not expiration_date_picker.value:
            self.show_message("Expiration date is required")
            return False

        # Validate initial quantity
        try:
            initial_quantity = int(initial_quantity_input.value)
            if initial_quantity <= 0:
                self.show_message("Initial quantity must be positive")
                return False
        except ValueError:
            self.show_message("Initial quantity must be a number")
            return False

        return True

    def handle_submit(self) -> None:
        """Handle the submit button being pressed."""
        if not self.validate_form():
            return

        # Get form values
        lot_number_input = self.query_one("#lot_number", Input)
        expiration_date_picker = self.query_one("#expiration_date", DatePicker)
        initial_quantity_input = self.query_one("#initial_quantity", Input)

        lot_number = lot_number_input.value
        expiration_date = expiration_date_picker.value
        initial_quantity = int(initial_quantity_input.value)

        try:
            with self.session_factory() as session:
                if self.lot:
                    # Update existing lot
                    update_lot(
                        session,
                        lot_number=lot_number,
                        expiration_date=expiration_date,
                        initial_quantity=initial_quantity,
                    )
                else:
                    # Create new lot
                    create_lot(
                        session,
                        lot_number=lot_number,
                        expiration_date=expiration_date,
                        initial_quantity=initial_quantity,
                    )
            self.dismiss(True)
        except IntegrityError:
            self.show_message("Error: Lot number already exists")
        except Exception as e:
            self.show_message(f"Error: {str(e)}")
