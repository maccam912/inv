# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Custom DatePicker widget for Textual."""

from datetime import date, timedelta
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label


class DatePicker(Widget):
    """A custom date picker widget for Textual UI."""

    DEFAULT_CSS = """
    DatePicker {
        width: 100%;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 0 1;
    }

    DatePicker > Horizontal {
        height: 3;
        align: center middle;
    }

    DatePicker Button {
        width: 3;
    }

    DatePicker Label {
        width: 1fr;
        content-align: center middle;
        text-style: bold;
    }
    """

    BINDINGS: ClassVar[list[Any]] = [
        Binding("left", "previous_day", "Previous Day", show=False),
        Binding("right", "next_day", "Next Day", show=False),
        Binding("up", "previous_month", "Previous Month", show=False),
        Binding("down", "next_month", "Next Month", show=False),
        Binding("pageup", "previous_year", "Previous Year", show=False),
        Binding("pagedown", "next_year", "Next Year", show=False),
    ]

    class Changed(Message):
        """Message sent when the date is changed."""

        def __init__(self, date_picker: "DatePicker", date_value: date) -> None:
            """Initialize the Changed message.

            Args:
                date_picker: The DatePicker that changed
                date_value: The new date value
            """
            self.date_picker = date_picker
            self.date_value = date_value
            super().__init__()

    _value = reactive(date.today())

    def __init__(
        self,
        value: date | None = None,
        id: str | None = None,
        classes: str | None = None,
        name: str | None = None,
    ) -> None:
        """Initialize the DatePicker.

        Args:
            value: The initial date value
            id: The widget ID
            classes: CSS classes
            name: The widget name
        """
        super().__init__(id=id, classes=classes, name=name)
        if value is not None:
            self._value = value

    def compose(self) -> ComposeResult:
        """Compose the DatePicker widget.

        Returns:
            The child widgets
        """
        with Horizontal():
            yield Button("<", id="prev-day", variant="primary")
            yield Label("", id="date-display")
            yield Button(">", id="next-day", variant="primary")

    def on_mount(self) -> None:
        """Set up the widget when mounted."""
        self._update_display()

    def _update_display(self) -> None:
        """Update the date display."""
        try:
            date_display = self.query_one("#date-display", Label)
            date_display.update(self._value.strftime("%Y-%m-%d"))
        except Exception:
            # Widget might not be mounted yet, we'll update on mount
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: The button press event
        """
        if event.button.id == "prev-day":
            self.action_previous_day()
        elif event.button.id == "next-day":
            self.action_next_day()

    def watch__value(self, value: date) -> None:
        """React to changes in the date value.

        Args:
            value: The new date value
        """
        self._update_display()
        self.post_message(self.Changed(self, value))

    def action_previous_day(self) -> None:
        """Move to the previous day."""
        self._value = self._value - timedelta(days=1)

    def action_next_day(self) -> None:
        """Move to the next day."""
        self._value = self._value + timedelta(days=1)

    def action_previous_month(self) -> None:
        """Move to the previous month."""
        year = self._value.year
        month = self._value.month - 1
        if month < 1:
            month = 12
            year -= 1
        # Handle month length differences
        day = min(self._value.day, 28)  # Start with a safe day
        while True:
            try:
                self._value = date(year, month, day)
                break
            except ValueError:
                day -= 1

    def action_next_month(self) -> None:
        """Move to the next month."""
        MONTHS_IN_YEAR = 12
        year = self._value.year
        month = self._value.month + 1
        if month > MONTHS_IN_YEAR:
            month = 1
            year += 1
        # Handle month length differences
        day = min(self._value.day, 28)  # Start with a safe day
        while True:
            try:
                self._value = date(year, month, day)
                break
            except ValueError:
                day -= 1

    def action_previous_year(self) -> None:
        """Move to the previous year."""
        FEBRUARY = 2
        LEAP_DAY = 29
        REGULAR_FEB_DAYS = 28

        year = self._value.year - 1
        month = self._value.month
        day = self._value.day

        # Handle February 29 in leap years
        if month == FEBRUARY and day == LEAP_DAY:
            day = REGULAR_FEB_DAYS

        self._value = date(year, month, day)

    def action_next_year(self) -> None:
        """Move to the next year."""
        FEBRUARY = 2
        LEAP_DAY = 29
        REGULAR_FEB_DAYS = 28

        year = self._value.year + 1
        month = self._value.month
        day = self._value.day

        # Handle February 29 in leap years
        if month == FEBRUARY and day == LEAP_DAY:
            day = REGULAR_FEB_DAYS

        self._value = date(year, month, day)

    @property
    def value(self) -> date:
        """Get the current date value.

        Returns:
            The current date
        """
        return self._value

    @value.setter
    def value(self, new_value: date) -> None:
        """Set the date value.

        Args:
            new_value: The new date value
        """
        self._value = new_value
