"""Report screen for generating inventory reports."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import date
from typing import Any, ClassVar

from sqlalchemy.orm import Session
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Label,
    Select,
    Static,
)

from inv.db.models import Inventory
from inv.db.operations import (
    calculate_usage_rate,
    predict_annual_usage,
    predict_leftover_quantity,
    predict_runout_date,
    read_inventory,
    read_lots,
    read_sites,
)


class ReportScreen(Container):
    """Screen for generating and viewing inventory reports."""

    REPORT_TYPES: ClassVar[list[tuple[str, str]]] = [
        ("stock_level", "Current Stock Levels"),
        ("expiration", "Upcoming Expirations"),
        ("usage", "Usage by Site"),
    ]

    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the ReportScreen.

        Args:
            session_factory: A context manager factory function to create database sessions
            *args: Additional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(*args, **kwargs)
        self.session_factory = session_factory
        self.report_table: DataTable | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the report screen."""
        yield Label("Report Generation", classes="title")

        with Vertical(id="report_controls"):
            yield Label("Select a report type:", classes="subtitle")
            yield Select(
                options=self.REPORT_TYPES,
                value="stock_level",
                id="report_select",
            )
            yield Button("Generate Report", id="generate_report", variant="primary")

        yield Label("Report Results", id="report_title", classes="subtitle")
        yield Static(
            "Select a report type and click 'Generate Report'.", id="report_description"
        )
        yield DataTable(id="report_table")

    def on_mount(self) -> None:
        """Set up the screen when it's mounted."""
        self.report_table = self.query_one("#report_table", DataTable)

    @on(Button.Pressed, "#generate_report")
    def handle_generate_report(self) -> None:
        """Handle the generate report button being pressed."""
        report_select = self.query_one("#report_select", Select)
        report_type = report_select.value

        if report_type == "stock_level":
            self.generate_stock_level_report()
        elif report_type == "expiration":
            self.generate_expiration_report()
        elif report_type == "usage":
            self.generate_usage_report()

    def generate_stock_level_report(self) -> None:
        """Generate a report of current stock levels across all sites."""
        # Clear existing table
        report_table = self.query_one("#report_table", DataTable)
        report_table.clear(columns=True)

        # Update description
        self.query_one("#report_title", Label).update("Current Stock Levels Report")
        self.query_one("#report_description", Static).update(
            "Showing current inventory levels for all lots across all sites."
        )

        # Set up columns
        report_table.add_columns(
            "Lot Number",
            "Site",
            "Current Quantity",
            "Last Updated",
            "Days Until Run-out",
        )

        # Get data from database
        with self.session_factory() as session:
            inventory_list = read_inventory(session)

            if not inventory_list:
                return

            # We need to handle the inventory_list type properly
            sorted_inventory = (
                inventory_list if isinstance(inventory_list, list) else [inventory_list]
            )

            # Sort manually (if there are multiple items)
            if len(sorted_inventory) > 1:
                sorted_inventory.sort(
                    key=lambda inv: (str(inv.lot_number), str(inv.site_name))
                )

            # Add rows to table
            for inv in sorted_inventory:
                runout_text = "Unknown"

                # Try to calculate days until runout
                try:
                    runout_date = predict_runout_date(
                        session, inv.lot_number, inv.site_name
                    )
                    if runout_date:
                        days_until_runout = (runout_date - date.today()).days
                        runout_text = f"{days_until_runout} days"
                except Exception:
                    pass

                report_table.add_row(
                    inv.lot_number,
                    inv.site_name,
                    str(inv.current_quantity),
                    str(inv.last_updated_date),
                    runout_text,
                )

    def generate_expiration_report(self) -> None:
        """Generate a report of upcoming lot expirations."""
        # Clear existing table
        report_table = self.query_one("#report_table", DataTable)
        report_table.clear(columns=True)

        # Update description
        self.query_one("#report_title", Label).update("Upcoming Expirations Report")
        self.query_one("#report_description", Static).update(
            "Showing upcoming expirations for all lots with remaining inventory."
        )

        # Set up columns
        report_table.add_columns(
            "Lot Number",
            "Expiration Date",
            "Days Until Expiration",
            "Total Remaining Inventory",
            "Expected Leftover",
        )

        # Get data from database
        with self.session_factory() as session:
            lots = read_lots(session)

            # Get inventory data for each lot
            report_data = []
            for lot in lots:
                # Find all inventory records for this lot
                inv_items = (
                    session.query(Inventory).filter_by(lot_number=lot.lot_number).all()
                )

                # Skip lots with no inventory
                if not inv_items:
                    continue

                # Calculate days until expiration
                days_until_expiration = (lot.expiration_date - date.today()).days

                # Calculate total remaining inventory
                total_remaining = sum(inv.current_quantity for inv in inv_items)

                # Calculate expected leftover across all sites
                total_leftover = 0
                for inv in inv_items:
                    leftover = predict_leftover_quantity(
                        session, inv.lot_number, inv.site_name
                    )
                    if leftover is not None:
                        total_leftover += leftover

                report_data.append(
                    {
                        "lot_number": lot.lot_number,
                        "expiration_date": lot.expiration_date,
                        "days_until_expiration": days_until_expiration,
                        "total_remaining": total_remaining,
                        "total_leftover": total_leftover,
                    }
                )

            # Sort by days until expiration (ascending)
            def get_days(x: dict[str, Any]) -> int:
                return int(x.get("days_until_expiration", 0))

            report_data.sort(key=get_days)

            # Add rows to table
            for data in report_data:
                report_table.add_row(
                    data["lot_number"],
                    str(data["expiration_date"]),
                    str(data["days_until_expiration"]),
                    str(data["total_remaining"]),
                    str(data["total_leftover"]),
                )

    def generate_usage_report(self) -> None:
        """Generate a report of usage statistics by site."""
        # Clear existing table
        report_table = self.query_one("#report_table", DataTable)
        report_table.clear(columns=True)

        # Update description
        self.query_one("#report_title", Label).update("Usage by Site Report")
        self.query_one("#report_description", Static).update(
            "Showing usage statistics for all lots across all sites."
        )

        # Set up columns
        report_table.add_columns(
            "Site",
            "Lot Number",
            "Daily Usage Rate",
            "Total Used",
            "Projected Annual Usage",
        )

        # Get data from database
        with self.session_factory() as session:
            sites = read_sites(session)
            lots = read_lots(session)

            # Prepare data for all site/lot combinations
            report_data = []
            for site in sites:
                for lot in lots:
                    # Check if this site has this lot in inventory
                    inventory = (
                        session.query(Inventory)
                        .filter_by(lot_number=lot.lot_number, site_name=site.site_name)
                        .first()
                    )

                    if not inventory:
                        continue

                    # Calculate usage rate
                    usage_info = calculate_usage_rate(
                        session, lot.lot_number, site.site_name
                    )

                    if not usage_info:
                        continue

                    daily_rate, total_used, _ = usage_info

                    # Calculate annual usage
                    annual_usage = predict_annual_usage(
                        session, lot.lot_number, site.site_name
                    )

                    report_data.append(
                        {
                            "site_name": site.site_name,
                            "lot_number": lot.lot_number,
                            "daily_rate": daily_rate,
                            "total_used": total_used,
                            "annual_usage": annual_usage,
                        }
                    )

            # Sort by site name, then lot number
            def get_sort_key(x: dict[str, Any]) -> tuple[str, str]:
                return (str(x.get("site_name", "")), str(x.get("lot_number", "")))

            report_data.sort(key=get_sort_key)

            # Add rows to table
            for data in report_data:
                annual_usage_text = "Unknown"
                if data["annual_usage"] is not None:
                    annual_usage_text = str(data["annual_usage"])

                report_table.add_row(
                    data["site_name"],
                    data["lot_number"],
                    f"{data['daily_rate']:.2f} units/day",
                    str(data["total_used"]),
                    annual_usage_text,
                )
