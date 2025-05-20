# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for inventory database operations."""

from datetime import date, timedelta

import pytest

from inv.db.models import Inventory, init_db
from inv.db.operations import (
    calculate_usage_rate,
    create_inventory,
    create_lot,
    create_shipment,
    create_site,
    predict_runout_date,
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


def test_calculate_usage_rate(test_db, test_lot_and_site):
    """Test calculating usage rate for a lot at a specific site."""
    lot_number, site_name = test_lot_and_site

    # Create a shipment from 30 days ago
    past_date = date.today() - timedelta(days=30)
    shipment = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=past_date,
        quantity_shipped=TEST_QUANTITY,
    )

    # Record arrival
    record_stock_arrival(test_db, shipment_id=shipment.shipment_id)

    # Record some usage (half of the quantity)
    usage_amount = TEST_QUANTITY // 2
    record_stock_usage(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        quantity_used=usage_amount,
    )

    # Calculate usage rate
    rate_info = calculate_usage_rate(
        test_db, lot_number=lot_number, site_name=site_name
    )

    assert rate_info is not None
    usage_rate, total_used, first_date = rate_info

    # Expected rate is usage_amount / 30 days
    expected_rate = usage_amount / 30
    assert usage_rate == pytest.approx(expected_rate)
    assert total_used == usage_amount
    assert first_date == past_date


def test_calculate_usage_rate_no_usage(test_db, test_lot_and_site):
    """Test calculating usage rate when no stock has been used."""
    lot_number, site_name = test_lot_and_site

    # Create a shipment
    shipment = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=date.today() - timedelta(days=10),
        quantity_shipped=TEST_QUANTITY,
    )

    # Record arrival (but no usage)
    record_stock_arrival(test_db, shipment_id=shipment.shipment_id)

    # Calculate usage rate
    rate_info = calculate_usage_rate(
        test_db, lot_number=lot_number, site_name=site_name
    )

    assert rate_info is not None
    usage_rate, total_used, first_date = rate_info

    # Since no usage occurred, rate should be 0
    assert usage_rate == 0.0
    assert total_used == 0
    assert first_date == shipment.shipment_date


def test_calculate_usage_rate_multiple_shipments(test_db, test_lot_and_site):
    """Test calculating usage rate with multiple shipments over time."""
    lot_number, site_name = test_lot_and_site

    # Create first shipment 60 days ago
    first_date = date.today() - timedelta(days=60)
    shipment1 = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=first_date,
        quantity_shipped=50,
    )

    # Record first arrival
    record_stock_arrival(test_db, shipment_id=shipment1.shipment_id)

    # Use some stock after first shipment
    record_stock_usage(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        quantity_used=30,
    )

    # Create second shipment 30 days ago
    shipment2 = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=date.today() - timedelta(days=30),
        quantity_shipped=50,
    )

    # Record second arrival
    record_stock_arrival(test_db, shipment_id=shipment2.shipment_id)

    # Use more stock after second shipment
    record_stock_usage(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        quantity_used=40,
    )

    # Calculate usage rate
    rate_info = calculate_usage_rate(
        test_db, lot_number=lot_number, site_name=site_name
    )

    assert rate_info is not None
    usage_rate, total_used, first_date = rate_info

    # Total shipped: 50 + 50 = 100
    # Total used: 30 + 40 = 70
    # Days elapsed: 60
    # Expected rate: 70 / 60 = 1.16667
    # Calculate expected values
    EXPECTED_TOTAL_USED = 30 + 40  # Sum of used quantities from lines 417 and 436
    DAYS_ELAPSED = 60
    expected_rate = EXPECTED_TOTAL_USED / DAYS_ELAPSED
    assert usage_rate == pytest.approx(expected_rate)
    assert total_used == EXPECTED_TOTAL_USED
    assert first_date == shipment1.shipment_date


def test_calculate_usage_rate_same_day(test_db, test_lot_and_site):
    """Test calculating usage rate when shipment and usage are on the same day."""
    lot_number, site_name = test_lot_and_site

    # Create a shipment for today
    shipment = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=date.today(),
        quantity_shipped=TEST_QUANTITY,
    )

    # Record arrival
    record_stock_arrival(test_db, shipment_id=shipment.shipment_id)

    # Use some stock
    record_stock_usage(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        quantity_used=10,
    )

    # Calculate usage rate - should return None since days_elapsed is 0
    rate_info = calculate_usage_rate(
        test_db, lot_number=lot_number, site_name=site_name
    )

    assert rate_info is None


def test_calculate_usage_rate_nonexistent_inventory(test_db):
    """Test calculating usage rate for non-existent inventory."""
    rate_info = calculate_usage_rate(
        test_db, lot_number="NONEXISTENT", site_name="NONEXISTENT"
    )
    assert rate_info is None


def test_calculate_usage_rate_no_shipments(test_db, test_lot_and_site):
    """Test calculating usage rate when no shipments exist."""
    lot_number, site_name = test_lot_and_site

    # Create inventory directly without shipments
    create_inventory(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=TEST_QUANTITY,
    )

    # Calculate usage rate
    rate_info = calculate_usage_rate(
        test_db, lot_number=lot_number, site_name=site_name
    )

    # Should return None since there are no shipments to establish history
    assert rate_info is None


def test_predict_runout_date(test_db, test_lot_and_site):
    """Test predicting run-out date for a lot at a specific site."""
    lot_number, site_name = test_lot_and_site

    # Create a shipment from 30 days ago
    past_date = date.today() - timedelta(days=30)
    shipment = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=past_date,
        quantity_shipped=TEST_QUANTITY,
    )

    # Record arrival
    record_stock_arrival(test_db, shipment_id=shipment.shipment_id)

    # Record some usage (half of the quantity)
    usage_amount = TEST_QUANTITY // 2
    record_stock_usage(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        quantity_used=usage_amount,
    )

    # Calculate run-out date
    runout_date = predict_runout_date(
        test_db, lot_number=lot_number, site_name=site_name
    )

    # Current inventory is TEST_QUANTITY - usage_amount
    # Usage rate is usage_amount / 30 days
    # Days until runout is (TEST_QUANTITY - usage_amount) / (usage_amount / 30)
    remaining_quantity = TEST_QUANTITY - usage_amount
    usage_rate = usage_amount / 30
    days_until_runout = int(remaining_quantity / usage_rate)
    expected_date = date.today() + timedelta(days=days_until_runout)

    assert runout_date is not None
    assert runout_date == expected_date


def test_predict_runout_date_no_usage(test_db, test_lot_and_site):
    """Test predicting run-out date when no stock has been used."""
    lot_number, site_name = test_lot_and_site

    # Create a shipment
    shipment = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=date.today() - timedelta(days=10),
        quantity_shipped=TEST_QUANTITY,
    )

    # Record arrival (but no usage)
    record_stock_arrival(test_db, shipment_id=shipment.shipment_id)

    # Calculate run-out date
    runout_date = predict_runout_date(
        test_db, lot_number=lot_number, site_name=site_name
    )

    # Since there's no usage, the inventory won't run out
    assert runout_date is None


def test_predict_runout_date_nonexistent_inventory(test_db):
    """Test predicting run-out date for non-existent inventory."""
    runout_date = predict_runout_date(
        test_db, lot_number="NONEXISTENT", site_name="NONEXISTENT"
    )
    assert runout_date is None


def test_predict_runout_date_same_day(test_db, test_lot_and_site):
    """Test predicting run-out date when shipment and usage are on the same day."""
    lot_number, site_name = test_lot_and_site

    # Create a shipment for today
    shipment = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=date.today(),
        quantity_shipped=TEST_QUANTITY,
    )

    # Record arrival
    record_stock_arrival(test_db, shipment_id=shipment.shipment_id)

    # Use some stock
    record_stock_usage(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        quantity_used=10,
    )

    # Calculate run-out date - should return None since usage rate can't be calculated
    runout_date = predict_runout_date(
        test_db, lot_number=lot_number, site_name=site_name
    )

    assert runout_date is None


def test_predict_runout_date_zero_inventory(test_db, test_lot_and_site):
    """Test predicting run-out date when inventory is already zero."""
    lot_number, site_name = test_lot_and_site

    # Create a shipment from 30 days ago
    past_date = date.today() - timedelta(days=30)
    shipment = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=past_date,
        quantity_shipped=TEST_QUANTITY,
    )

    # Record arrival
    record_stock_arrival(test_db, shipment_id=shipment.shipment_id)

    # Use all stock
    record_stock_usage(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        quantity_used=TEST_QUANTITY,
    )

    # Calculate run-out date
    runout_date = predict_runout_date(
        test_db, lot_number=lot_number, site_name=site_name
    )

    # Since inventory is already empty, run-out date is today
    assert runout_date == date.today()


def test_predict_runout_date_multiple_shipments(test_db, test_lot_and_site):
    """Test predicting run-out date with multiple shipments over time."""
    lot_number, site_name = test_lot_and_site

    # Create first shipment 60 days ago
    first_date = date.today() - timedelta(days=60)
    shipment1 = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=first_date,
        quantity_shipped=50,
    )

    # Record first arrival
    record_stock_arrival(test_db, shipment_id=shipment1.shipment_id)

    # Use some stock after first shipment
    record_stock_usage(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        quantity_used=30,
    )

    # Create second shipment 30 days ago
    shipment2 = create_shipment(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=date.today() - timedelta(days=30),
        quantity_shipped=50,
    )

    # Record second arrival
    record_stock_arrival(test_db, shipment_id=shipment2.shipment_id)

    # Use more stock after second shipment
    record_stock_usage(
        test_db,
        lot_number=lot_number,
        site_name=site_name,
        quantity_used=40,
    )

    # Calculate run-out date
    runout_date = predict_runout_date(
        test_db, lot_number=lot_number, site_name=site_name
    )

    # Total shipped: 50 + 50 = 100
    # Total used: 30 + 40 = 70
    # Current inventory: 30
    # Usage rate: 70 / 60 = 1.1667 units per day
    # Days until runout: 30 / 1.1667 = 25.71 days (rounded to 25)
    remaining_quantity = 100 - 70  # 30
    usage_rate = 70 / 60  # 1.1667
    days_until_runout = int(remaining_quantity / usage_rate)  # 25
    expected_date = date.today() + timedelta(days=days_until_runout)

    assert runout_date is not None
    assert runout_date == expected_date
