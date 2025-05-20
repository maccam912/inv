from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from inv.tui.dashboard import Dashboard


class InventoryApp(App):
    """A Textual application to manage inventory."""

    TITLE = "Inventory Management"
    CSS_PATH = None
    
    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle dark mode", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]
    
    dark: bool = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Dashboard(id="dashboard")
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = InventoryApp()
    app.run()
