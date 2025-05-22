# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for database operation edge cases and error handling."""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from inv.db.models import Inventory, Lot, Shipment, Site, init_db
from inv.db.operations import (
    create_inventory,
    create_lot,
    create_shipment,
    create_site,
    delete_lot,
    delete_shipment,
    delete_site,
    read_inventory,
    read_lot,
    read_shipments,
    update_inventory_quantity,
    update_lot,
    update_shipment,
    update_site,
)

# Constants for testing
TEST_QUANTITY = 100


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    Session = init_db("sqlite:///:memory:")
    session = Session()
    yield session
    session.close()


def test_update_lot_integrity_error(test_db):
    """Test handling of IntegrityError during lot update."""
    # Create a lot
    create_lot(
        test_db,
        lot_number="LOT-INTEGRITY-1",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=TEST_QUANTITY,
    )

    # Create another lot
    create_lot(
        test_db,
        lot_number="LOT-INTEGRITY-2",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=TEST_QUANTITY,
    )

    # Mock the commit method to raise IntegrityError
    with patch.object(test_db, "commit", side_effect=IntegrityError("mock", "mock", "mock")):
        with pytest.raises(IntegrityError):
            update_lot(
                test_db,
                lot_number="LOT-INTEGRITY-1",
                expiration_date=date.today() + timedelta(days=90),
            )


def test_delete_lot_integrity_error(test_db):
    """Test handling of IntegrityError during lot deletion."""
    # Create a lot
    create_lot(
        test_db,
        lot_number="LOT-DELETE-1",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=TEST_QUANTITY,
    )

    # Mock the commit method to raise IntegrityError
    with patch.object(test_db, "commit", side_effect=IntegrityError("mock", "mock", "mock")):
        with pytest.raises(IntegrityError):
            delete_lot(test_db, lot_number="LOT-DELETE-1")


def test_update_site_integrity_error(test_db):
    """Test handling of IntegrityError during site update."""
    # Create a site
    create_site(test_db, site_name="SITE-INTEGRITY-1", contact_info="Test Contact")

    # Mock the commit method to raise IntegrityError
    with patch.object(test_db, "commit", side_effect=IntegrityError("mock", "mock", "mock")):
        with pytest.raises(IntegrityError):
            update_site(test_db, site_name="SITE-INTEGRITY-1", contact_info="Updated Contact")


def test_delete_site_integrity_error(test_db):
    """Test handling of IntegrityError during site deletion."""
    # Create a site
    create_site(test_db, site_name="SITE-DELETE-1", contact_info="Test Contact")

    # Mock the commit method to raise IntegrityError
    with patch.object(test_db, "commit", side_effect=IntegrityError("mock", "mock", "mock")):
        with pytest.raises(IntegrityError):
            delete_site(test_db, site_name="SITE-DELETE-1")


def test_update_shipment_integrity_error(test_db):
    """Test handling of IntegrityError during shipment update."""
    # Create a lot and site
    create_lot(
        test_db,
        lot_number="LOT-SHIP-1",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=TEST_QUANTITY,
    )
    create_site(test_db, site_name="SITE-SHIP-1", contact_info="Test Contact")

    # Create a shipment
    shipment = create_shipment(
        test_db,
        lot_number="LOT-SHIP-1",
        site_name="SITE-SHIP-1",
        shipment_date=date.today(),
        quantity_shipped=50,
    )

    # Mock the commit method to raise IntegrityError
    with patch.object(test_db, "commit", side_effect=IntegrityError("mock", "mock", "mock")):
        with pytest.raises(IntegrityError):
            update_shipment(
                test_db,
                shipment_id=shipment.shipment_id,
                quantity_shipped=75,
            )


def test_delete_shipment_integrity_error(test_db):
    """Test handling of IntegrityError during shipment deletion."""
    # Create a lot and site
    create_lot(
        test_db,
        lot_number="LOT-SHIP-DELETE",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=TEST_QUANTITY,
    )
    create_site(test_db, site_name="SITE-SHIP-DELETE", contact_info="Test Contact")

    # Create a shipment
    shipment = create_shipment(
        test_db,
        lot_number="LOT-SHIP-DELETE",
        site_name="SITE-SHIP-DELETE",
        shipment_date=date.today(),
        quantity_shipped=50,
    )

    # Mock the commit method to raise IntegrityError
    with patch.object(test_db, "commit", side_effect=IntegrityError("mock", "mock", "mock")):
        with pytest.raises(IntegrityError):
            delete_shipment(test_db, shipment_id=shipment.shipment_id)


def test_update_lot_nonexistent(test_db):
    """Test updating a non-existent lot."""
    result = update_lot(
        test_db,
        lot_number="NONEXISTENT-LOT",
        expiration_date=date.today() + timedelta(days=90),
    )
    assert result is None


def test_update_site_nonexistent(test_db):
    """Test updating a non-existent site."""
    result = update_site(
        test_db,
        site_name="NONEXISTENT-SITE",
        contact_info="Updated Contact",
    )
    assert result is None


def test_delete_lot_nonexistent(test_db):
    """Test deleting a non-existent lot."""
    result = delete_lot(test_db, lot_number="NONEXISTENT-LOT")
    assert result is False


def test_delete_site_nonexistent(test_db):
    """Test deleting a non-existent site."""
    result = delete_site(test_db, site_name="NONEXISTENT-SITE")
    assert result is False


def test_update_shipment_nonexistent(test_db):
    """Test updating a non-existent shipment."""
    result = update_shipment(
        test_db,
        shipment_id=999,
        quantity_shipped=75,
    )
    assert result is None


def test_delete_shipment_nonexistent(test_db):
    """Test deleting a non-existent shipment."""
    result = delete_shipment(test_db, shipment_id=999)
    assert result is False


def test_read_shipments_multiple_filters(test_db):
    """Test reading shipments with multiple filters."""
    # Create lots and sites
    create_lot(
        test_db,
        lot_number="LOT-MULTI-1",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=TEST_QUANTITY,
    )
    create_lot(
        test_db,
        lot_number="LOT-MULTI-2",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=TEST_QUANTITY,
    )
    create_site(test_db, site_name="SITE-MULTI-1", contact_info="Contact 1")
    create_site(test_db, site_name="SITE-MULTI-2", contact_info="Contact 2")

    # Create shipments
    create_shipment(
        test_db,
        lot_number="LOT-MULTI-1",
        site_name="SITE-MULTI-1",
        shipment_date=date.today() - timedelta(days=10),
        quantity_shipped=50,
    )
    create_shipment(
        test_db,
        lot_number="LOT-MULTI-1",
        site_name="SITE-MULTI-2",
        shipment_date=date.today() - timedelta(days=5),
        quantity_shipped=50,
    )
    create_shipment(
        test_db,
        lot_number="LOT-MULTI-2",
        site_name="SITE-MULTI-1",
        shipment_date=date.today(),
        quantity_shipped=50,
    )

    # Test filtering by lot and site
    shipments = read_shipments(
        test_db,
        lot_number="LOT-MULTI-1",
        site_name="SITE-MULTI-1",
    )
    assert len(shipments) == 1
    assert shipments[0].lot_number == "LOT-MULTI-1"
    assert shipments[0].site_name == "SITE-MULTI-1"

    # Test filtering by just lot
    shipments = read_shipments(
        test_db,
        lot_number="LOT-MULTI-1",
    )
    assert len(shipments) == 2
    assert all(s.lot_number == "LOT-MULTI-1" for s in shipments)

    # Test filtering by just site
    shipments = read_shipments(
        test_db,
        site_name="SITE-MULTI-1",
    )
    assert len(shipments) == 2
    assert all(s.site_name == "SITE-MULTI-1" for s in shipments)

    # Test with no filters
    shipments = read_shipments(test_db)
    assert len(shipments) == 3


def test_update_inventory_zero_quantity(test_db):
    """Test updating inventory to exactly zero quantity."""
    # Create lot and site
    create_lot(
        test_db,
        lot_number="LOT-ZERO",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=TEST_QUANTITY,
    )
    create_site(test_db, site_name="SITE-ZERO", contact_info="Test Contact")

    # Create inventory
    inventory = create_inventory(
        test_db,
        lot_number="LOT-ZERO",
        site_name="SITE-ZERO",
        current_quantity=TEST_QUANTITY,
    )

    # Update to zero (should be allowed)
    updated = update_inventory_quantity(
        test_db,
        inventory_id=inventory.inventory_id,
        quantity_change=-TEST_QUANTITY,
    )

    assert updated is not None
    assert updated.current_quantity == 0

    # Verify in database
    result = read_inventory(test_db, inventory_id=inventory.inventory_id)
    assert result.current_quantity == 0