# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for the dashboard warnings functionality."""

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine

from inv.db.models import Base, init_db
from inv.db.operations import (
    create_lot,
    create_shipment,
    create_site,
    record_stock_arrival,
    record_stock_usage,
)
from inv.tui.dashboard import Dashboard

# Constants for testing
TEST_QUANTITY = 100
TEST_USAGE = 40
TEST_DAYS_BEFORE_EXPIRY = 10
REMAINING_QUANTITY = TEST_QUANTITY - TEST_USAGE
LOW_INV_SHIPMENT_QUANTITY = 50
LOW_INV_REMAINING = LOW_INV_SHIPMENT_QUANTITY - TEST_USAGE  # 10


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


def test_dashboard_init():
    """Test that dashboard initializes correctly."""
    # Create dashboard without session_factory
    dashboard = Dashboard()
    assert dashboard.session_factory is None

    # Create dashboard with session_factory
    mock_factory = MagicMock()
    dashboard = Dashboard(mock_factory)
    assert dashboard.session_factory is mock_factory


def test_dashboard_warnings_expiring_lots(test_db, mock_session_factory):
    """Test that dashboard correctly identifies lots nearing expiration."""
    # Create dashboard with session factory
    dashboard = Dashboard(mock_session_factory)

    # Create a lot that's expiring soon (within EXPIRING_SOON_DAYS)
    soon_expiry = date.today() + timedelta(days=TEST_DAYS_BEFORE_EXPIRY)
    create_lot(
        test_db,
        lot_number="EXPIRING-SOON",
        expiration_date=soon_expiry,
        initial_quantity=TEST_QUANTITY,
    )

    # Create a lot that's not expiring soon
    future_expiry = date.today() + timedelta(days=dashboard.EXPIRING_SOON_DAYS + 10)
    create_lot(
        test_db,
        lot_number="NOT-EXPIRING-SOON",
        expiration_date=future_expiry,
        initial_quantity=TEST_QUANTITY,
    )

    # Get warnings
    warnings = dashboard.get_expiring_lots()

    # Check results
    assert len(warnings) == 1
    assert warnings[0]["lot_number"] == "EXPIRING-SOON"
    assert warnings[0]["days"] == TEST_DAYS_BEFORE_EXPIRY
    assert warnings[0]["date"] == soon_expiry


def test_dashboard_warnings_low_inventory(test_db, mock_session_factory):
    """Test that dashboard correctly identifies inventory running low."""
    # Create dashboard with session factory
    dashboard = Dashboard(mock_session_factory)

    # Create a lot and site
    test_lot = "LOW-INV-LOT"
    test_site = "LOW-INV-SITE"

    expiry = date.today() + timedelta(days=60)
    create_lot(
        test_db,
        lot_number=test_lot,
        expiration_date=expiry,
        initial_quantity=TEST_QUANTITY,
    )
    create_site(test_db, site_name=test_site)

    # Create a shipment from 10 days ago
    past_date = date.today() - timedelta(days=10)
    shipment = create_shipment(
        test_db,
        lot_number=test_lot,
        site_name=test_site,
        shipment_date=past_date,
        quantity_shipped=LOW_INV_SHIPMENT_QUANTITY,
    )

    # Record arrival
    record_stock_arrival(test_db, shipment_id=shipment.shipment_id)

    # Use some stock to establish a usage rate (40 units over 10 days = 4 units/day)
    # At this rate, remaining 10 units will last about 2.5 days
    record_stock_usage(
        test_db, lot_number=test_lot, site_name=test_site, quantity_used=TEST_USAGE
    )

    # Get warnings
    warnings = dashboard.get_low_inventory()

    # Check results
    assert len(warnings) == 1
    assert warnings[0]["lot_number"] == test_lot
    assert warnings[0]["site_name"] == test_site
    assert warnings[0]["days"] <= dashboard.LOW_INVENTORY_DAYS
    assert warnings[0]["current_quantity"] == LOW_INV_REMAINING


def test_dashboard_warnings_slow_moving(test_db, mock_session_factory):
    """Test that dashboard correctly identifies slow-moving inventory."""
    # Create dashboard with session factory
    dashboard = Dashboard(mock_session_factory)

    # Create a lot and site
    test_lot = "SLOW-MOVING-LOT"
    test_site = "SLOW-MOVING-SITE"

    expiry = date.today() + timedelta(days=30)
    create_lot(
        test_db,
        lot_number=test_lot,
        expiration_date=expiry,
        initial_quantity=TEST_QUANTITY,
    )
    create_site(test_db, site_name=test_site)

    # Create a shipment from 30 days ago
    past_date = date.today() - timedelta(days=30)
    shipment = create_shipment(
        test_db,
        lot_number=test_lot,
        site_name=test_site,
        shipment_date=past_date,
        quantity_shipped=TEST_QUANTITY,
    )

    # Record arrival
    record_stock_arrival(test_db, shipment_id=shipment.shipment_id)

    # Use very little stock to establish a slow usage rate (10 units over 30 days = 0.33 units/day)
    # At this rate, with 30 days until expiry, we expect to use only 10 more units
    # leaving 80 units leftover (80% of initial quantity)
    record_stock_usage(
        test_db, lot_number=test_lot, site_name=test_site, quantity_used=10
    )

    # Get warnings
    warnings = dashboard.get_slow_moving_inventory()

    # Check results
    assert len(warnings) == 1
    assert warnings[0]["lot_number"] == test_lot
    assert warnings[0]["site_name"] == test_site
    assert warnings[0]["percent_leftover"] >= (dashboard.SLOW_MOVING_THRESHOLD * 100)
