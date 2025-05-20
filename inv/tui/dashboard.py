# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
from textual.containers import Container
from textual.widgets import Static


class Dashboard(Container):
    """A placeholder dashboard for the main inventory view."""

    def compose(self):
        """Create child widgets for the dashboard."""
        yield Static("Welcome to the Inventory Management Dashboard", id="welcome")
        yield Static("This is a placeholder for the main dashboard view.", id="info")