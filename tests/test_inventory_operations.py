# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for inventory database operations."""

from datetime import date, timedelta

import pytest

from inv.db.models import Inventory, init_db
from inv.db.operations import (
    create_inventory,
    create_lot,
    create_shipment,
    create_site,
    read_inventories,
    read_inventory,
    record_stock_arrival,
    record_stock_usage,
    update_inventory_quantity,
)

# Constants for testing
TEST_QUANTITY = 100
USAGE_QUANTITY = 20
SHIPMENT_QUANTITY = 50


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    Session = init_db("sqlite:///:memory:")
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_lot_and_site(test_db):
    """Create a test lot and site for inventory tests."""
    # Create a lot and site
    create_lot(
        test_db,
        lot_number="TEST-LOT-1",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=TEST_QUANTITY,
    )
    create_site(test_db, site_name="TEST-SITE-1", contact_info="Test Contact")
    return "TEST-LOT-1", "TEST-SITE-1"


def test_create_inventory(test_db, test_lot_and_site):
    """Test creating an inventory record using the create_inventory function."""
    lot_number, site_name = test_lot_and_site

    inventory = create_inventory(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=TEST_QUANTITY,
    )

    assert inventory.inventory_id is not None
    assert inventory.lot_number == lot_number
    assert inventory.site_name == site_name
    assert inventory.current_quantity == TEST_QUANTITY
    assert inventory.last_updated_date == date.today()

    # Verify in database
    result = (
        test_db.query(Inventory).filter_by(inventory_id=inventory.inventory_id).first()
    )
    assert result is not None
    assert result.lot_number == lot_number
    assert result.site_name == site_name
    assert result.current_quantity == TEST_QUANTITY


def test_read_inventory_by_id(test_db, test_lot_and_site):
    """Test reading an inventory record by ID."""
    lot_number, site_name = test_lot_and_site

    # Create an inventory record first
    inventory = create_inventory(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=TEST_QUANTITY,
    )

    # Read by ID
    result = read_inventory(test_db, inventory_id=inventory.inventory_id)
    assert result is not None
    assert result.inventory_id == inventory.inventory_id
    assert result.lot_number == lot_number
    assert result.site_name == site_name
    assert result.current_quantity == TEST_QUANTITY


def test_read_inventory_by_lot_and_site(test_db, test_lot_and_site):
    """Test reading an inventory record by lot number and site name."""
    lot_number, site_name = test_lot_and_site

    # Create an inventory record first
    create_inventory(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=TEST_QUANTITY,
    )

    # Read by lot number and site name
    result = read_inventory(test_db, lot_number=lot_number, site_name=site_name)
    assert result is not None
    assert result.lot_number == lot_number
    assert result.site_name == site_name
    assert result.current_quantity == TEST_QUANTITY


def test_read_inventories(test_db, test_lot_and_site):
    """Test reading all inventory records."""
    lot_number, site_name = test_lot_and_site

    # Create a second lot and site
    create_lot(
        test_db,
        lot_number="TEST-LOT-2",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=TEST_QUANTITY,
    )
    create_site(test_db, site_name="TEST-SITE-2", contact_info="Test Contact 2")

    # Create inventory records
    create_inventory(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=TEST_QUANTITY,
    )
    create_inventory(
        test_db,
        lot_number="TEST-LOT-2",
        site_name="TEST-SITE-2",
        current_quantity=TEST_QUANTITY,
    )

    # Read all inventories
    results = read_inventories(test_db)
    EXPECTED_INVENTORY_COUNT = 2
    assert len(results) == EXPECTED_INVENTORY_COUNT

    # Read by lot number
    results = read_inventories(test_db, lot_number=lot_number)
    assert len(results) == 1
    assert results[0].lot_number == lot_number

    # Read by site name
    results = read_inventories(test_db, site_name="TEST-SITE-2")
    assert len(results) == 1
    assert results[0].site_name == "TEST-SITE-2"


def test_update_inventory_quantity(test_db, test_lot_and_site):
    """Test updating the quantity of an inventory record."""
    lot_number, site_name = test_lot_and_site

    # Create an inventory record first
    inventory = create_inventory(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=TEST_QUANTITY,
    )

    # Update quantity (increase)
    updated = update_inventory_quantity(
        test_db, inventory_id=inventory.inventory_id, quantity_change=50
    )
    assert updated.current_quantity == TEST_QUANTITY + 50
    assert updated.last_updated_date == date.today()

    # Update quantity (decrease)
    updated = update_inventory_quantity(
        test_db, inventory_id=inventory.inventory_id, quantity_change=-30
    )
    assert updated.current_quantity == TEST_QUANTITY + 50 - 30
    assert updated.last_updated_date == date.today()


def test_update_inventory_quantity_invalid(test_db, test_lot_and_site):
    """Test updating the quantity with invalid values."""
    lot_number, site_name = test_lot_and_site

    # Create an inventory record first
    inventory = create_inventory(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=TEST_QUANTITY,
    )

    # Try to update with a quantity change that would make it negative
    with pytest.raises(ValueError):
        update_inventory_quantity(
            test_db,
            inventory_id=inventory.inventory_id,
            quantity_change=-(TEST_QUANTITY + 1),
        )

    # Verify quantity wasn't changed
    result = read_inventory(test_db, inventory_id=inventory.inventory_id)
    assert result.current_quantity == TEST_QUANTITY


def test_record_stock_arrival(test_db, test_lot_and_site):
    """Test recording stock arrival from a shipment."""
    lot_number, site_name = test_lot_and_site

    # Create a shipment
    shipment = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=date.today(),
        quantity_shipped=SHIPMENT_QUANTITY,
    )

    # Record arrival
    inventory = record_stock_arrival(test_db, shipment_id=shipment.shipment_id)

    assert inventory is not None
    assert inventory.lot_number == lot_number
    assert inventory.site_name == site_name
    assert inventory.current_quantity == SHIPMENT_QUANTITY
    assert inventory.last_updated_date == date.today()

    # Create another shipment
    shipment2 = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=date.today(),
        quantity_shipped=SHIPMENT_QUANTITY,
    )

    # Record another arrival
    inventory = record_stock_arrival(test_db, shipment_id=shipment2.shipment_id)

    assert inventory is not None
    assert inventory.current_quantity == SHIPMENT_QUANTITY * 2


def test_record_stock_arrival_invalid_shipment(test_db):
    """Test recording arrival for a non-existent shipment."""
    result = record_stock_arrival(test_db, shipment_id=999)
    assert result is None


def test_record_stock_usage(test_db, test_lot_and_site):
    """Test recording stock usage."""
    lot_number, site_name = test_lot_and_site

    # Create an inventory record first
    create_inventory(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=TEST_QUANTITY,
    )

    # Record usage
    inventory = record_stock_usage(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        quantity_used=USAGE_QUANTITY,
    )

    assert inventory is not None
    assert inventory.current_quantity == TEST_QUANTITY - USAGE_QUANTITY
    assert inventory.last_updated_date == date.today()


def test_record_stock_usage_invalid_quantity(test_db, test_lot_and_site):
    """Test recording usage with invalid quantities."""
    lot_number, site_name = test_lot_and_site

    # Create an inventory record first
    create_inventory(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=TEST_QUANTITY,
    )

    # Try to use negative quantity
    with pytest.raises(ValueError):
        record_stock_usage(
            test_db,
            lot_number=lot_number,
            site_name=site_name,
            quantity_used=-10,
        )

    # Try to use more than available
    with pytest.raises(ValueError):
        record_stock_usage(
            test_db,
            lot_number=lot_number,
            site_name=site_name,
            quantity_used=TEST_QUANTITY + 1,
        )

    # Verify quantity wasn't changed
    inventory = read_inventory(test_db, lot_number=lot_number, site_name=site_name)
    assert inventory.current_quantity == TEST_QUANTITY


def test_record_stock_usage_nonexistent_inventory(test_db):
    """Test recording usage for a non-existent inventory record."""
    result = record_stock_usage(
        test_db,
        lot_number="NONEXISTENT-LOT",
        site_name="NONEXISTENT-SITE",
        quantity_used=10,
    )
    assert result is None
