"""Tests for the lot screen."""

from collections.abc import Generator
from contextlib import contextmanager
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from inv.db.models import Lot
from inv.tui.lot_screen import LotScreen


@contextmanager
def mock_session() -> Generator[MagicMock, None, None]:
    """Create a mock session for testing."""
    session = MagicMock(spec=Session)
    try:
        yield session
    finally:
        pass


@pytest.fixture
def sample_lots() -> list[Lot]:
    """Return a list of sample lot objects for testing."""
    today = date.today()

    lot1 = Lot(
        lot_number="LOT001",
        expiration_date=today - timedelta(days=10),  # Expired
        initial_quantity=100,
    )

    lot2 = Lot(
        lot_number="LOT002",
        expiration_date=today + timedelta(days=20),  # Expiring soon
        initial_quantity=200,
    )

    lot3 = Lot(
        lot_number="LOT003",
        expiration_date=today + timedelta(days=60),  # Not expiring soon
        initial_quantity=300,
    )

    return [lot1, lot2, lot3]


def test_lot_screen_creation() -> None:
    """Test creating a LotScreen instance."""
    lot_screen = LotScreen(mock_session)
    assert lot_screen is not None


def test_get_expiration_status() -> None:
    """Test the _get_expiration_status method."""
    lot_screen = LotScreen(mock_session)
    today = date.today()

    # Test expired status
    expired_date = today - timedelta(days=1)
    assert lot_screen._get_expiration_status(expired_date) == "(EXPIRED)"

    # Test expiring soon status
    expiring_soon_date = today + timedelta(days=lot_screen.EXPIRING_SOON_DAYS - 1)
    assert lot_screen._get_expiration_status(expiring_soon_date) == "(EXPIRING SOON)"

    # Test no status for far future date
    future_date = today + timedelta(days=lot_screen.EXPIRING_SOON_DAYS + 10)
    assert lot_screen._get_expiration_status(future_date) == ""
