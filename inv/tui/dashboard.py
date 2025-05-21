# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Dashboard for displaying inventory warnings and status."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Label, Static

from inv.db.operations import (
    predict_leftover_quantity,
    predict_runout_date,
    read_inventories,
    read_lot,
    read_lots,
)


class Dashboard(Container):
    """Dashboard for showing inventory warnings and status information."""

    # Constants
    EXPIRING_SOON_DAYS = 30  # Days until expiration to show warning
    LOW_INVENTORY_DAYS = 30  # Days until run-out to show warning
    SLOW_MOVING_THRESHOLD = 0.2  # Percentage of initial quantity that will be leftover

    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the dashboard.

        Args:
            session_factory: Factory function for creating database sessions
            *args: Additional positional arguments for the parent class
            **kwargs: Additional keyword arguments for the parent class
        """
        super().__init__(*args, **kwargs)
        self.session_factory = session_factory

    def compose(self) -> ComposeResult:
        """Create child widgets for the dashboard."""
        yield Static("Welcome to the Inventory Management Dashboard", id="welcome")

        # Container for warnings
        with VerticalScroll(id="warnings_container"):
            yield Label("Loading warnings...", id="warnings_info")

    def on_mount(self) -> None:
        """Set up the dashboard when it's mounted."""
        if self.session_factory is not None:
            self.refresh_warnings()
        else:
            self.query_one("#warnings_info", Label).update(
                "Database connection not available"
            )

    def refresh_warnings(self) -> None:
        """Refresh the warnings displayed on the dashboard."""
        # Reset the warnings container
        warnings_container = self.query_one("#warnings_container", VerticalScroll)
        warnings_container.remove_children()

        if self.session_factory is None:
            warnings_container.mount(
                Label("Database connection not available", id="warnings_info")
            )
            return

        # Get warnings from database
        expiring_lots = self.get_expiring_lots()
        low_inventory = self.get_low_inventory()
        slow_moving = self.get_slow_moving_inventory()

        # Add warning sections
        warnings_container.mount(
            Label("## Inventory Warnings", classes="warning_heading")
        )

        # Expiring lots section
        warnings_container.mount(
            Label("### Lots Nearing Expiration", classes="warning_subheading")
        )
        if expiring_lots:
            for lot_info in expiring_lots:
                warnings_container.mount(
                    Label(
                        f"⚠️ Lot {lot_info['lot_number']} expires in {lot_info['days']} days "
                        f"({lot_info['date']})",
                        classes="warning_item",
                    )
                )
        else:
            warnings_container.mount(
                Label("No lots expiring soon.", classes="no_warning")
            )

        # Low inventory section
        warnings_container.mount(
            Label("### Low Inventory", classes="warning_subheading")
        )
        if low_inventory:
            for inv_info in low_inventory:
                warnings_container.mount(
                    Label(
                        f"⚠️ Lot {inv_info['lot_number']} at {inv_info['site_name']} "
                        f"will run out in {inv_info['days']} days ({inv_info['date']})",
                        classes="warning_item",
                    )
                )
        else:
            warnings_container.mount(
                Label("No sites running low on inventory.", classes="no_warning")
            )

        # Slow-moving inventory section
        warnings_container.mount(
            Label("### Slow-Moving Inventory", classes="warning_subheading")
        )
        if slow_moving:
            for inv_info in slow_moving:
                warnings_container.mount(
                    Label(
                        f"⚠️ Lot {inv_info['lot_number']} at {inv_info['site_name']} "
                        f"will have {inv_info['leftover']} units leftover at expiration "
                        f"({inv_info['percent_leftover']}% of initial quantity)",
                        classes="warning_item",
                    )
                )
        else:
            warnings_container.mount(
                Label("No slow-moving inventory identified.", classes="no_warning")
            )

    def get_expiring_lots(self) -> list[dict[str, Any]]:
        """
        Get lots that are nearing their expiration date.

        Returns:
            List of dictionaries with lot information
        """
        result: list[dict[str, Any]] = []

        if self.session_factory is None:
            return result

        with self.session_factory() as session:
            today = date.today()
            expiry_cutoff = today + timedelta(days=self.EXPIRING_SOON_DAYS)

            # Get lots that expire within the next EXPIRING_SOON_DAYS
            lots = read_lots(session, expired=False, expiration_before=expiry_cutoff)

            for lot in lots:
                days_until_expiry = (lot.expiration_date - today).days
                if 0 < days_until_expiry <= self.EXPIRING_SOON_DAYS:
                    result.append(
                        {
                            "lot_number": lot.lot_number,
                            "date": lot.expiration_date,
                            "days": days_until_expiry,
                        }
                    )

        # Sort by days until expiry (ascending)
        return sorted(result, key=lambda x: x["days"])

    def get_low_inventory(self) -> list[dict[str, Any]]:
        """
        Get inventory items that are predicted to run out soon.

        Returns:
            List of dictionaries with inventory information
        """
        result: list[dict[str, Any]] = []

        if self.session_factory is None:
            return result

        with self.session_factory() as session:
            inventories = read_inventories(session)

            for inv in inventories:
                if inv.current_quantity > 0:
                    runout_date = predict_runout_date(
                        session, lot_number=inv.lot_number, site_name=inv.site_name
                    )

                    if runout_date:
                        days_until_runout = (runout_date - date.today()).days
                        if 0 < days_until_runout <= self.LOW_INVENTORY_DAYS:
                            result.append(
                                {
                                    "lot_number": inv.lot_number,
                                    "site_name": inv.site_name,
                                    "current_quantity": inv.current_quantity,
                                    "date": runout_date,
                                    "days": days_until_runout,
                                }
                            )

        # Sort by days until runout (ascending)
        return sorted(result, key=lambda x: x["days"])

    def get_slow_moving_inventory(self) -> list[dict[str, Any]]:
        """
        Get inventory items that are not being used quickly enough
        and will likely have leftover stock at expiration.

        Returns:
            List of dictionaries with inventory information
        """
        result: list[dict[str, Any]] = []

        if self.session_factory is None:
            return result

        with self.session_factory() as session:
            inventories = read_inventories(session)

            for inv in inventories:
                if inv.current_quantity > 0:
                    leftover = predict_leftover_quantity(
                        session, lot_number=inv.lot_number, site_name=inv.site_name
                    )

                    # Check if there will be significant leftovers
                    if leftover is not None and leftover > 0:
                        # Get the specific lot
                        lot = read_lot(session, lot_number=inv.lot_number)
                        if lot:
                            percent_leftover = round(
                                (leftover / lot.initial_quantity) * 100, 1
                            )

                            if percent_leftover >= (self.SLOW_MOVING_THRESHOLD * 100):
                                result.append(
                                    {
                                        "lot_number": inv.lot_number,
                                        "site_name": inv.site_name,
                                        "leftover": leftover,
                                        "percent_leftover": percent_leftover,
                                    }
                                )

        # Sort by percent leftover (descending)
        return sorted(result, key=lambda x: x["percent_leftover"], reverse=True)
