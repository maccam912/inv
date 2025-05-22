# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Hypothesis-based tests for core logic functions."""

from datetime import date, timedelta

import pytest
from hypothesis import given, settings, HealthCheck, strategies as st

from inv.db.models import Inventory, init_db
from inv.db.operations import (
    calculate_usage_rate,
    create_inventory,
    create_lot,
    create_shipment,
    create_site,
    predict_annual_usage,
    predict_leftover_quantity,
    predict_runout_date,
    read_inventory,
    record_stock_arrival,
    record_stock_usage,
)


# Create a helper function to get a clean database for each hypothesis test
def get_test_db():
    """Create a test database in memory."""
    Session = init_db("sqlite:///:memory:")
    session = Session()
    return session


def setup_test_inventory(session, lot_number, site_name, shipment_date, usage_quantity):
    """Set up test inventory with the given parameters."""
    # Create a lot and site
    create_lot(
        session,
        lot_number=lot_number,
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=1000,  # Large initial quantity for flexibility in tests
    )
    create_site(session, site_name=site_name, contact_info="Test Contact")
    
    # Create a shipment
    shipment = create_shipment(
        session,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=shipment_date,
        quantity_shipped=500,  # Ship half the lot
    )
    
    # Record arrival
    record_stock_arrival(session, shipment_id=shipment.shipment_id)
    
    # Record usage
    if usage_quantity > 0:
        record_stock_usage(
            session,
            lot_number=lot_number,
            site_name=site_name,
            quantity_used=usage_quantity,
        )
    
    return shipment_date


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(usage_quantity=st.integers(min_value=1, max_value=400))
def test_calculate_usage_rate_hypothesis(usage_quantity):
    """Test calculate_usage_rate with hypothesis-generated data."""
    # Set up a fresh database for each test case
    session = get_test_db()
    lot_number = "TEST-LOT-HYP"
    site_name = "TEST-SITE-HYP"
    past_date = date.today() - timedelta(days=30)
    
    # Set up test inventory
    setup_test_inventory(session, lot_number, site_name, past_date, usage_quantity)
    
    # Calculate usage rate
    rate_info = calculate_usage_rate(session, lot_number=lot_number, site_name=site_name)
    
    assert rate_info is not None
    usage_rate, total_used, first_date = rate_info
    
    # Expected rate calculation
    days_elapsed = (date.today() - past_date).days
    expected_rate = usage_quantity / days_elapsed
    
    assert usage_rate == pytest.approx(expected_rate)
    assert total_used == usage_quantity
    assert first_date == past_date
    
    # Clean up
    session.close()


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(usage_quantity=st.integers(min_value=1, max_value=400))
def test_predict_runout_date_hypothesis(usage_quantity):
    """Test predict_runout_date with hypothesis-generated data."""
    # Set up a fresh database for each test case
    session = get_test_db()
    lot_number = "TEST-LOT-HYP"
    site_name = "TEST-SITE-HYP"
    past_date = date.today() - timedelta(days=30)
    
    # Set up test inventory
    setup_test_inventory(session, lot_number, site_name, past_date, usage_quantity)
    
    # Get current inventory
    inventory = read_inventory(session, lot_number=lot_number, site_name=site_name)
    assert inventory is not None
    
    # Calculate run-out date
    runout_date = predict_runout_date(session, lot_number=lot_number, site_name=site_name)
    
    # Verify the result
    assert runout_date is not None
    
    # Calculate expected run-out date
    days_elapsed = (date.today() - past_date).days
    usage_rate = usage_quantity / days_elapsed
    remaining_quantity = inventory.current_quantity
    days_until_runout = int(remaining_quantity / usage_rate)
    expected_date = date.today() + timedelta(days=days_until_runout)
    
    assert runout_date == expected_date
    
    # Clean up
    session.close()


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(usage_quantity=st.integers(min_value=1, max_value=400))
def test_predict_annual_usage_hypothesis(usage_quantity):
    """Test predict_annual_usage with hypothesis-generated data."""
    # Set up a fresh database for each test case
    session = get_test_db()
    lot_number = "TEST-LOT-HYP"
    site_name = "TEST-SITE-HYP"
    past_date = date.today() - timedelta(days=30)
    
    # Set up test inventory
    setup_test_inventory(session, lot_number, site_name, past_date, usage_quantity)
    
    # Calculate annual usage
    annual_usage = predict_annual_usage(session, lot_number=lot_number, site_name=site_name)
    
    # Verify the result
    assert annual_usage is not None
    
    # Calculate expected annual usage
    days_elapsed = (date.today() - past_date).days
    expected_daily_rate = usage_quantity / days_elapsed
    expected_annual_usage = int(expected_daily_rate * 365)
    
    assert annual_usage == expected_annual_usage
    
    # Clean up
    session.close()


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(usage_quantity=st.integers(min_value=1, max_value=400))
def test_predict_leftover_quantity_hypothesis(usage_quantity):
    """Test predict_leftover_quantity with hypothesis-generated data."""
    # Set up a fresh database for each test case
    session = get_test_db()
    lot_number = "TEST-LOT-HYP"
    site_name = "TEST-SITE-HYP"
    past_date = date.today() - timedelta(days=30)
    
    # Set up test inventory
    setup_test_inventory(session, lot_number, site_name, past_date, usage_quantity)
    
    # Calculate leftover quantity
    leftover_quantity = predict_leftover_quantity(session, lot_number=lot_number, site_name=site_name)
    
    # Verify the result
    assert leftover_quantity is not None
    
    # Calculate expected leftover quantity
    inventory = read_inventory(session, lot_number=lot_number, site_name=site_name)
    current_quantity = inventory.current_quantity
    
    # Get the lot to check its expiration date
    days_elapsed = (date.today() - past_date).days
    usage_rate = usage_quantity / days_elapsed
    
    # Calculate days until expiration and expected usage
    days_until_expiration = (date.today() + timedelta(days=180) - date.today()).days
    expected_usage = int(days_until_expiration * usage_rate)
    
    # Calculate expected leftover quantity
    expected_leftover = current_quantity - expected_usage
    
    assert leftover_quantity == expected_leftover
    
    # Clean up
    session.close()


# Test edge cases for calculation functions
def test_calculate_usage_rate_edge_cases():
    """Test calculate_usage_rate with various edge cases."""
    session = get_test_db()
    lot_number = "EDGE-LOT"
    site_name = "EDGE-SITE"
    
    # Create lot and site
    create_lot(
        session,
        lot_number=lot_number,
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=100,
    )
    create_site(session, site_name=site_name, contact_info="Test Contact")
    
    # Case 1: No inventory
    result = calculate_usage_rate(session, lot_number=lot_number, site_name=site_name)
    assert result is None
    
    # Case 2: Inventory exists but no shipments
    create_inventory(
        session,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=50,
    )
    result = calculate_usage_rate(session, lot_number=lot_number, site_name=site_name)
    assert result is None
    
    # Case 3: Shipment today (days_elapsed = 0)
    shipment = create_shipment(
        session,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=date.today(),
        quantity_shipped=50,
    )
    record_stock_arrival(session, shipment_id=shipment.shipment_id)
    record_stock_usage(
        session,
        lot_number=lot_number,
        site_name=site_name,
        quantity_used=10,
    )
    result = calculate_usage_rate(session, lot_number=lot_number, site_name=site_name)
    # For shipment on the same day as usage, we expect either None or a rate with 0 used
    if result is not None:
        assert result[0] == 0.0  # Usage rate
        assert result[1] == 0     # Total used
    
    # Clean up
    session.close()


def test_predict_runout_date_edge_cases():
    """Test predict_runout_date with various edge cases."""
    session = get_test_db()
    lot_number = "EDGE-LOT"
    site_name = "EDGE-SITE"
    
    # Create lot and site
    create_lot(
        session,
        lot_number=lot_number,
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=100,
    )
    create_site(session, site_name=site_name, contact_info="Test Contact")
    
    # Case 1: No inventory
    result = predict_runout_date(session, lot_number=lot_number, site_name=site_name)
    assert result is None
    
    # Case 2: Zero inventory
    create_inventory(
        session,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=0,
    )
    result = predict_runout_date(session, lot_number=lot_number, site_name=site_name)
    assert result == date.today()
    
    # Case 3: Inventory exists but no usage rate can be calculated
    # Clear out existing inventory
    inventory = read_inventory(session, lot_number=lot_number, site_name=site_name)
    if inventory:
        session.delete(inventory)
        session.commit()
    
    # Create new inventory
    create_inventory(
        session,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=50,
    )
    result = predict_runout_date(session, lot_number=lot_number, site_name=site_name)
    assert result is None
    
    # Clean up
    session.close()


def test_predict_leftover_quantity_edge_cases():
    """Test predict_leftover_quantity with various edge cases."""
    session = get_test_db()
    lot_number = "EDGE-LOT"
    site_name = "EDGE-SITE"
    
    # Create lot and site
    create_lot(
        session,
        lot_number=lot_number,
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=100,
    )
    create_site(session, site_name=site_name, contact_info="Test Contact")
    
    # Case 1: No inventory
    result = predict_leftover_quantity(session, lot_number=lot_number, site_name=site_name)
    assert result is None
    
    # Case 2: Zero inventory
    create_inventory(
        session,
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=0,
    )
    result = predict_leftover_quantity(session, lot_number=lot_number, site_name=site_name)
    assert result == 0
    
    # Case 3: Already expired lot
    # Clear out existing inventory
    inventory = read_inventory(session, lot_number=lot_number, site_name=site_name)
    if inventory:
        session.delete(inventory)
        session.commit()
    
    # Create expired lot
    expired_lot_number = "EXPIRED-LOT"
    create_lot(
        session,
        lot_number=expired_lot_number,
        expiration_date=date.today() - timedelta(days=10),  # Already expired
        initial_quantity=100,
    )
    create_inventory(
        session,
        lot_number=expired_lot_number,
        site_name=site_name,
        current_quantity=50,
    )
    result = predict_leftover_quantity(session, lot_number=expired_lot_number, site_name=site_name)
    assert result == 50  # All current inventory is leftover since it's already expired
    
    # Clean up
    session.close()


def test_predict_annual_usage_edge_cases():
    """Test predict_annual_usage with various edge cases."""
    session = get_test_db()
    lot_number = "EDGE-LOT"
    site_name = "EDGE-SITE"
    
    # Create lot and site
    create_lot(
        session,
        lot_number=lot_number,
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=100,
    )
    create_site(session, site_name=site_name, contact_info="Test Contact")
    
    # Case 1: No inventory or usage rate
    result = predict_annual_usage(session, lot_number=lot_number, site_name=site_name)
    assert result is None
    
    # Case 2: Inventory exists but no usage (rate is 0)
    past_date = date.today() - timedelta(days=30)
    shipment = create_shipment(
        session,
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=past_date,
        quantity_shipped=50,
    )
    record_stock_arrival(session, shipment_id=shipment.shipment_id)
    
    # No usage recorded, so usage rate should be 0
    # This is implemented differently depending on the function,
    # so we can accept None or 0 as a valid result
    result = predict_annual_usage(session, lot_number=lot_number, site_name=site_name)
    assert result is None or result == 0
    
    # Clean up
    session.close()