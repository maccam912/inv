"""Tests for the site screen."""

from collections.abc import Generator
from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from inv.db.models import Site
from inv.tui.site_screen import SiteScreen


@contextmanager
def mock_session() -> Generator[MagicMock, None, None]:
    """Create a mock session for testing."""
    session = MagicMock(spec=Session)
    try:
        yield session
    finally:
        pass


@pytest.fixture
def sample_sites() -> list[Site]:
    """Return a list of sample site objects for testing."""
    site1 = Site(
        site_name="SITE001",
        contact_info="Contact Info 1",
    )

    site2 = Site(
        site_name="SITE002",
        contact_info=None,
    )

    site3 = Site(
        site_name="SITE003",
        contact_info="Contact Info 3",
    )

    return [site1, site2, site3]


def test_site_screen_creation() -> None:
    """Test creating a SiteScreen instance."""
    site_screen = SiteScreen(mock_session)
    assert site_screen is not None