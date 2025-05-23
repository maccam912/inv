# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Site Form for adding and editing sites."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Label

from inv.db.models import Site
from inv.db.operations import create_site, read_site, update_site
from inv.tui.forms import FormScreen, create_text_field


class SiteForm(FormScreen):
    """Form for adding or editing sites."""

    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        site_name: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the site form.

        Args:
            session_factory: A factory function to create database sessions
            site_name: The site name to edit (None for adding a new site)
            *args: Additional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        title = "Edit Site" if site_name else "Add New Site"
        super().__init__(session_factory, title, *args, **kwargs)
        self.site_name = site_name
        self.site: Site | None = None

        if site_name:
            with self.session_factory() as session:
                self.site = read_site(session, site_name)

    def _compose_form(self) -> ComposeResult:
        """Create form fields for the site form."""
        with Vertical():
            if self.site:
                # Editing an existing site
                # Create site name field (read-only in edit mode)
                yield Label("Site Name:", classes="field-label")
                yield Input(
                    value=self.site.site_name,
                    placeholder="Enter site name",
                    id="site_name",
                    classes="input-field",
                    disabled=True,  # Make it read-only directly
                )

                # Create contact info field
                yield from create_text_field(
                    "contact_info",
                    "Contact Information:",
                    value=self.site.contact_info or "",
                    placeholder="Enter contact information",
                )
            else:
                # Adding a new site
                yield from create_text_field(
                    "site_name",
                    "Site Name:",
                    placeholder="Enter site name",
                )
                yield from create_text_field(
                    "contact_info",
                    "Contact Information:",
                    placeholder="Enter contact information",
                )

    def validate_form(self) -> bool:
        """
        Validate the form inputs.

        Returns:
            True if validation passes, False otherwise
        """
        # Get form values
        site_name_input = self.query_one("#site_name", Input)

        # Validate site name
        if not site_name_input.value:
            self.show_message("Site name is required")
            return False

        return True

    def handle_submit(self) -> None:
        """Handle the submit button being pressed."""
        if not self.validate_form():
            return

        # Get form values
        site_name_input = self.query_one("#site_name", Input)
        contact_info_input = self.query_one("#contact_info", Input)

        site_name = site_name_input.value
        contact_info = contact_info_input.value or None

        try:
            with self.session_factory() as session:
                if self.site:
                    # Update existing site
                    update_site(
                        session,
                        site_name=site_name,
                        contact_info=contact_info,
                    )
                else:
                    # Create new site
                    create_site(
                        session,
                        site_name=site_name,
                        contact_info=contact_info,
                    )
            self.dismiss(True)
        except IntegrityError:
            self.show_message("Error: Site name already exists")
            return  # Early return to prevent further processing
        except Exception as e:
            self.show_message(f"Error: {str(e)}")
            return  # Early return to prevent further processing
