from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session, sessionmaker
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from inv.db.models import init_db
from inv.tui.dashboard import Dashboard
from inv.tui.lot_screen import LotScreen


class InventoryApp(App):
    """A Textual application to manage inventory."""

    TITLE = "Inventory Management"
    CSS_PATH = None

    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle dark mode", show=True),
        Binding("l", "show_lots", "Show Lots", show=True),
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
        yield Dashboard(id="dashboard")
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_show_lots(self) -> None:
        """An action to show the lots screen."""
        self.query_one("#dashboard").remove()
        lot_screen = LotScreen(self.get_session, id="lot_screen")
        self.mount(lot_screen)

    def action_back_to_dashboard(self) -> None:
        """An action to return to the dashboard."""
        # Only act if we're not already on the dashboard
        if self.query("Dashboard") == []:
            # Try to find and remove the lot screen if it exists
            lot_screen = self.query("LotScreen")
            if lot_screen:
                lot_screen[0].remove()

            # Mount the dashboard
            self.mount(Dashboard(id="dashboard"))


if __name__ == "__main__":
    app = InventoryApp()
    app.run()
