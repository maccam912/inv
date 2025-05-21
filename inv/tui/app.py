from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session, sessionmaker
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, TabbedContent, TabPane

from inv.db.models import init_db
from inv.tui.dashboard import Dashboard
from inv.tui.inventory_screen import InventoryScreen
from inv.tui.lot_screen import LotScreen
from inv.tui.report_screen import ReportScreen
from inv.tui.shipment_screen import ShipmentScreen
from inv.tui.site_screen import SiteScreen


class InventoryApp(App):
    """A Textual application to manage inventory."""

    TITLE = "Inventory Management"
    CSS_PATH = "app.css"

    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle dark mode", show=True),
        Binding("l", "show_lots", "Show Lots", show=True),
        Binding("s", "show_sites", "Show Sites", show=True),
        Binding("h", "show_shipments", "Show Shipments", show=True),
        Binding("i", "show_inventory", "Show Inventory", show=True),
        Binding("r", "show_reports", "Show Reports", show=True),
        Binding("b", "back_to_dashboard", "Back to Dashboard", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    dark: bool = False

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the application."""
        super().__init__(*args, **kwargs)
        # Initialize the database
        self.Session: sessionmaker = init_db()  # This returns a sessionmaker

    @contextmanager
    def get_session(self) -> Iterator[Session]:
        """
        Get a database session as a context manager.

        This ensures the session is properly closed after use.

        Yields:
            A database session
        """
        session = self.Session()
        try:
            yield session
        finally:
            session.close()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        # Create a tabbed interface with different screens
        with TabbedContent(id="screen_tabs"):
            with TabPane("Dashboard", id="dashboard_tab"):
                yield Dashboard(self.get_session, id="dashboard")
            with TabPane("Lot Management", id="lot_tab"):
                yield LotScreen(self.get_session, id="lot_screen")
            with TabPane("Site Management", id="site_tab"):
                yield SiteScreen(self.get_session, id="site_screen")
            with TabPane("Shipment Management", id="shipment_tab"):
                yield ShipmentScreen(self.get_session, id="shipment_screen")
            with TabPane("Inventory Tracking", id="inventory_tab"):
                yield InventoryScreen(self.get_session, id="inventory_screen")
            with TabPane("Reports", id="report_tab"):
                yield ReportScreen(self.get_session, id="report_screen")
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_show_lots(self) -> None:
        """An action to show the lots screen."""
        tabs = self.query_one("#screen_tabs", TabbedContent)
        tabs.active = "lot_tab"

    def action_show_sites(self) -> None:
        """An action to show the sites screen."""
        tabs = self.query_one("#screen_tabs", TabbedContent)
        tabs.active = "site_tab"

    def action_show_shipments(self) -> None:
        """An action to show the shipments screen."""
        tabs = self.query_one("#screen_tabs", TabbedContent)
        tabs.active = "shipment_tab"

    def action_show_inventory(self) -> None:
        """An action to show the inventory screen."""
        tabs = self.query_one("#screen_tabs", TabbedContent)
        tabs.active = "inventory_tab"

    def action_show_reports(self) -> None:
        """An action to show the reports screen."""
        tabs = self.query_one("#screen_tabs", TabbedContent)
        tabs.active = "report_tab"

    def action_back_to_dashboard(self) -> None:
        """An action to return to the dashboard."""
        tabs = self.query_one("#screen_tabs", TabbedContent)
        tabs.active = "dashboard_tab"


if __name__ == "__main__":
    app = InventoryApp()
    app.run()
