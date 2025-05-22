"""Tests for the report screen functionality."""

from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine

from inv.db.models import Base, init_db
from inv.tui.report_screen import ReportScreen


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    session_factory = init_db("sqlite:///:memory:")
    session = session_factory()

    yield session

    session.close()


@pytest.fixture
def mock_session_factory(test_db):
    """Create a session factory that returns the test database session."""

    class ContextManager:
        def __enter__(self):
            return test_db

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    return lambda: ContextManager()


def test_report_screen_init():
    """Test report screen initialization."""
    # Create report screen without session_factory
    report_screen = ReportScreen(MagicMock())

    # Check report types are defined
    expected_report_count = 3
    assert len(report_screen.REPORT_TYPES) == expected_report_count
    assert report_screen.REPORT_TYPES[0][1] == "stock_level"
    assert report_screen.REPORT_TYPES[1][1] == "expiration"
    assert report_screen.REPORT_TYPES[2][1] == "usage"


def test_report_screen_with_session(mock_session_factory):
    """Test report screen with session factory."""
    report_screen = ReportScreen(mock_session_factory)
    # Check that the session factory is set
    assert report_screen.session_factory is mock_session_factory


def test_report_generation_methods(mock_session_factory, monkeypatch):
    """Test that report generation methods exist."""
    report_screen = ReportScreen(mock_session_factory)

    # Monkeypatch the generation methods to avoid actual DB operations
    monkeypatch.setattr(report_screen, "query_one", MagicMock())

    # Test that methods exist
    assert hasattr(report_screen, "generate_stock_level_report")
    assert hasattr(report_screen, "generate_expiration_report")
    assert hasattr(report_screen, "generate_usage_report")

    # Call the methods to make sure they're callable
    report_screen.generate_stock_level_report()
    report_screen.generate_expiration_report()
    report_screen.generate_usage_report()
