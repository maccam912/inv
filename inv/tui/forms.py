# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Form components for data entry and editing."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import date
from typing import Any

from sqlalchemy.orm import Session
from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static

# Import DatePicker from wherever it's available in the current Textual version
try:
    from textual.widgets._date_picker import DatePicker
except ImportError:
    try:
        from textual.widgets.date_picker import DatePicker
    except ImportError:
        # Fallback to a mock DatePicker for testing
        from textual.widget import Widget

        class _DatePickerMock(Widget):
            """Mock DatePicker for testing."""

            def __init__(
                self, id: str | None = None, classes: str | None = None
            ) -> None:
                super().__init__(id=id, classes=classes)
                self._value = date.today()

            @property
            def value(self) -> date:
                return self._value

            @value.setter
            def value(self, new_value: date) -> None:
                self._value = new_value

        DatePicker = _DatePickerMock


class FormScreen(ModalScreen):
    """Base class for form screens."""

    DEFAULT_CSS = """
    FormScreen {
        align: center middle;
    }

    .form-container {
        background: $panel;
        padding: 1 2;
        border: tall $primary;
        width: 60;
        height: auto;
    }

    .form-container Label.title {
        text-align: center;
        text-style: bold;
        width: 100%;
        margin-bottom: 1;
    }

    .form-container Label.field-label {
        width: 100%;
        margin-top: 1;
        margin-bottom: 1;
    }

    .input-field {
        width: 100%;
        margin-bottom: 1;
    }

    .date-field {
        width: 100%;
        margin-bottom: 1;
    }

    .select-field {
        width: 100%;
        margin-bottom: 1;
    }

    .message {
        color: $error;
        margin-bottom: 1;
        height: 1;
    }

    .buttons {
        width: 100%;
        align-horizontal: right;
        margin-top: 1;
    }

    .buttons Button {
        margin-left: 1;
    }
    """

    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        title: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the form screen.

        Args:
            session_factory: A factory function to create database sessions
            title: The title of the form
            *args: Additional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(*args, **kwargs)
        self.session_factory = session_factory
        self.title = title
        self.message = ""

    def compose(self) -> ComposeResult:
        """Create child widgets for the form screen."""
        with Container(classes="form-container"):
            yield Label(self.title or "", classes="title")
            yield Static(self.message, id="message", classes="message")
            yield from self._compose_form()
            with Container(classes="buttons"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Submit", variant="primary", id="submit")

    def _compose_form(self) -> ComposeResult:
        """
        Create form fields.

        This method should be overridden by subclasses to add specific form fields.
        """
        yield Static("Override this method in subclasses")

    def show_message(self, message: str) -> None:
        """
        Show a message in the form.

        Args:
            message: The message to show
        """
        message_widget = self.query_one("#message", Static)
        message_widget.update(message)

    @on(Button.Pressed, "#cancel")
    def handle_cancel(self) -> None:
        """Handle the cancel button being pressed."""
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.

        Args:
            event: The button press event
        """
        if event.button.id == "submit":
            self.handle_submit()

    def handle_submit(self) -> None:
        """
        Handle the submit button being pressed.

        This method should be overridden by subclasses to validate and process form data.
        """
        self.show_message("Override this method in subclasses")


def create_text_field(
    id_: str, label: str, value: str = "", placeholder: str = ""
) -> list[Any]:
    """
    Create a text input field with a label.

    Args:
        id_: The ID for the input field
        label: The label text
        value: The initial value
        placeholder: Placeholder text for the input

    Returns:
        A list containing the label and input widgets
    """
    return [
        Label(label, classes="field-label"),
        Input(
            value=value,
            placeholder=placeholder,
            id=id_,
            classes="input-field",
        ),
    ]


def create_number_field(
    id_: str, label: str, value: int = 0, placeholder: str = ""
) -> list[Any]:
    """
    Create a number input field with a label.

    Args:
        id_: The ID for the input field
        label: The label text
        value: The initial value
        placeholder: Placeholder text for the input

    Returns:
        A list containing the label and input widgets
    """
    return [
        Label(label, classes="field-label"),
        Input(
            value=str(value),
            placeholder=placeholder,
            id=id_,
            classes="input-field",
        ),
    ]


def create_date_field(id_: str, label: str, value: date | None = None) -> list[Any]:
    """
    Create a date input field with a label.

    Args:
        id_: The ID for the input field
        label: The label text
        value: The initial value

    Returns:
        A list containing the label and datepicker widgets
    """
    date_picker = DatePicker(id=id_, classes="date-field")
    if value:
        date_picker.value = value
    else:
        date_picker.value = date.today()

    return [Label(label, classes="field-label"), date_picker]


def create_select_field(
    id_: str, label: str, options: list[tuple[Any, str]], value: Any = None
) -> list[Any]:
    """
    Create a select field with a label.

    Args:
        id_: The ID for the select field
        label: The label text
        options: A list of (value, label) tuples for the options
        value: The initial value

    Returns:
        A list containing the label and select widgets
    """
    return [
        Label(label, classes="field-label"),
        Select(
            options=options,
            value=value,
            id=id_,
            classes="select-field",
        ),
    ]
