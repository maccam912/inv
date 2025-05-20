# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Lot Management Screen for viewing lot information."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import date
from typing import Any

from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Label

from inv.db.operations import read_lots


class LotScreen(Container):
    """A screen for viewing and managing lots."""

    # Constants
    EXPIRING_SOON_DAYS = 30

    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the LotScreen.

        Args:
            session_factory: A context manager factory function to create database sessions
            *args: Additional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(*args, **kwargs)
        self.session_factory = session_factory
        self.lots_table: DataTable | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the lot screen."""
        yield Label("Lot Management", classes="title")
        yield DataTable(id="lots_table")
        # No need for the help text - it's in the footer now

    def on_mount(self) -> None:
        """Set up the screen when it's mounted."""
        self.lots_table = self.query_one("#lots_table", DataTable)
        self.lots_table.add_columns("Lot Number", "Expiration Date", "Initial Quantity")
        self.refresh_lots()

    def refresh_lots(self) -> None:
        """Refresh the lots table with data from the database."""
        self.lots_table = self.query_one("#lots_table", DataTable)
        self.lots_table.clear()

        with self.session_factory() as session:
            lots = read_lots(session)

            # Sort lots by expiration date
            lots.sort(key=lambda lot: lot.expiration_date)

            # Add rows for each lot
            for lot in lots:
                expiration_status = self._get_expiration_status(lot.expiration_date)
                self.lots_table.add_row(
                    lot.lot_number,
                    f"{lot.expiration_date} {expiration_status}",
                    str(lot.initial_quantity),
                    key=lot.lot_number,
                )

    def _get_expiration_status(self, expiration_date: date) -> str:
        """
        Get a status indicator for the expiration date.

        Args:
            expiration_date: The expiration date of the lot

        Returns:
            A string indicating the expiration status
        """
        today = date.today()
        if expiration_date < today:
            return "(EXPIRED)"
        elif (expiration_date - today).days <= self.EXPIRING_SOON_DAYS:
            return "(EXPIRING SOON)"
        return ""
