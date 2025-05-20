# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for the shipment screen."""

from contextlib import contextmanager
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from inv.tui.shipment_screen import ShipmentScreen


@contextmanager
def mock_session_factory(mock_session):
    """Create a mock session factory."""
    try:
        yield mock_session
    finally:
        pass


def test_shipment_screen_basic():
    """Test that the shipment screen initializes correctly."""
    # Create a mock session
    mock_session = MagicMock(spec=Session)

    # Create a screen with the mock session factory
    screen = ShipmentScreen(lambda: mock_session_factory(mock_session))

    # Assert the screen has the expected attributes
    assert screen.shipments_table is None
    assert hasattr(screen, "session_factory")
    assert callable(screen.session_factory)
