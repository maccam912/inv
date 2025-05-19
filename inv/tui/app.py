from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class InventoryApp(App):
    """A Textual application to manage inventory."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    dark: bool = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = InventoryApp()
    app.run()
