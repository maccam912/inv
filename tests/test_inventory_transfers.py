# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for inventory transfer suggestion functionality."""

from datetime import date, timedelta

import pytest

from inv.db.models import init_db
from inv.db.operations import (
    calculate_usage_rate,
    create_inventory,
    create_lot,
    create_shipment,
    create_site,
    predict_leftover_quantity,
    predict_runout_date,
    read_lot,
    record_stock_arrival,
    record_stock_usage,
    suggest_inventory_transfers,
)


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    Session = init_db("sqlite:///:memory:")
    session = Session()
    yield session
    session.close()


def test_suggest_inventory_transfers_no_suggestions(test_db):
    """Test that no transfers are suggested when there's no applicable inventory."""
    # Create a lot and sites
    create_lot(
        test_db,
        lot_number="TEST-LOT-1",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=100,
    )
    create_site(test_db, site_name="SITE-A", contact_info="Test Contact A")
    create_site(test_db, site_name="SITE-B", contact_info="Test Contact B")

    # Create inventory at both sites with sufficient quantities
    # No usage recorded, so no transfers should be suggested
    create_inventory(
        test_db,
        lot_number="TEST-LOT-1",
        site_name="SITE-A",
        current_quantity=50,
    )
    create_inventory(
        test_db,
        lot_number="TEST-LOT-1",
        site_name="SITE-B",
        current_quantity=50,
    )

    suggestions = suggest_inventory_transfers(test_db)
    assert len(suggestions) == 0


def test_suggest_inventory_transfers_with_suggestions(test_db):
    """Test that transfers are suggested when appropriate."""
    # Create a lot and sites
    create_lot(
        test_db,
        lot_number="TEST-LOT-1",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=100,
    )
    create_site(test_db, site_name="SITE-A", contact_info="Test Contact A")
    create_site(test_db, site_name="SITE-B", contact_info="Test Contact B")

    # Create shipments to both sites, 30 days ago
    past_date = date.today() - timedelta(days=30)
    shipment_a = create_shipment(
        test_db,
        lot_number="TEST-LOT-1",
        site_name="SITE-A",
        shipment_date=past_date,
        quantity_shipped=60,
    )
    shipment_b = create_shipment(
        test_db,
        lot_number="TEST-LOT-1",
        site_name="SITE-B",
        shipment_date=past_date,
        quantity_shipped=40,
    )

    # Record arrivals
    record_stock_arrival(test_db, shipment_id=shipment_a.shipment_id)
    record_stock_arrival(test_db, shipment_id=shipment_b.shipment_id)

    # Site A has high usage rate (will run out in less than 30 days)
    # Use 40 out of 60 units in 30 days (usage rate = 1.33 units per day)
    record_stock_usage(
        test_db,
        lot_number="TEST-LOT-1",
        site_name="SITE-A",
        quantity_used=40,
    )

    # Site B has low usage rate (will have surplus)
    # Use 5 out of 40 units in 30 days (usage rate = 0.167 units per day)
    record_stock_usage(
        test_db,
        lot_number="TEST-LOT-1",
        site_name="SITE-B",
        quantity_used=5,
    )

    # Get transfer suggestions
    suggestions = suggest_inventory_transfers(test_db)

    # Print debugging information
    print("\n=== Debugging Info ===")
    # Check if Site A is considered low
    runout_date_a = predict_runout_date(test_db, "TEST-LOT-1", "SITE-A")
    rate_info_a = calculate_usage_rate(test_db, "TEST-LOT-1", "SITE-A")
    print(f"Site A runout date: {runout_date_a}")
    print(f"Site A usage rate: {rate_info_a}")

    # Check if Site B has surplus
    leftover_b = predict_leftover_quantity(test_db, "TEST-LOT-1", "SITE-B")
    lot = read_lot(test_db, "TEST-LOT-1")
    if leftover_b is not None and lot is not None:
        percent_leftover = leftover_b / lot.initial_quantity
        print(f"Site B leftover: {leftover_b}")
        print(f"Site B percent leftover: {percent_leftover}")

    print("=== End Debugging ===\n")

    # Should suggest a transfer from Site B to Site A
    assert len(suggestions) == 1
    suggestion = suggestions[0]

    assert suggestion.lot_number == "TEST-LOT-1"
    assert suggestion.source_site == "SITE-B"
    assert suggestion.destination_site == "SITE-A"
    assert suggestion.quantity > 0
    assert suggestion.days_extended > 0


def test_suggest_inventory_transfers_multiple_lots(test_db):
    """Test that transfers are suggested for multiple lots."""
    # Create two lots and sites
    create_lot(
        test_db,
        lot_number="LOT-1",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=100,
    )
    create_lot(
        test_db,
        lot_number="LOT-2",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=100,
    )
    create_site(test_db, site_name="SITE-A", contact_info="Test Contact A")
    create_site(test_db, site_name="SITE-B", contact_info="Test Contact B")
    create_site(test_db, site_name="SITE-C", contact_info="Test Contact C")

    # Create shipments of both lots to all sites, 30 days ago
    past_date = date.today() - timedelta(days=30)

    # LOT-1 shipments
    shipment_lot1_a = create_shipment(
        test_db,
        lot_number="LOT-1",
        site_name="SITE-A",
        shipment_date=past_date,
        quantity_shipped=50,
    )
    shipment_lot1_b = create_shipment(
        test_db,
        lot_number="LOT-1",
        site_name="SITE-B",
        shipment_date=past_date,
        quantity_shipped=50,
    )

    # LOT-2 shipments
    shipment_lot2_b = create_shipment(
        test_db,
        lot_number="LOT-2",
        site_name="SITE-B",
        shipment_date=past_date,
        quantity_shipped=50,
    )
    shipment_lot2_c = create_shipment(
        test_db,
        lot_number="LOT-2",
        site_name="SITE-C",
        shipment_date=past_date,
        quantity_shipped=50,
    )

    # Record arrivals
    record_stock_arrival(test_db, shipment_id=shipment_lot1_a.shipment_id)
    record_stock_arrival(test_db, shipment_id=shipment_lot1_b.shipment_id)
    record_stock_arrival(test_db, shipment_id=shipment_lot2_b.shipment_id)
    record_stock_arrival(test_db, shipment_id=shipment_lot2_c.shipment_id)

    # Set up usage patterns:
    # LOT-1 at SITE-A: High usage (will run out soon)
    record_stock_usage(
        test_db,
        lot_number="LOT-1",
        site_name="SITE-A",
        quantity_used=40,  # Usage rate: 1.33 units/day
    )

    # LOT-1 at SITE-B: Low usage (surplus)
    record_stock_usage(
        test_db,
        lot_number="LOT-1",
        site_name="SITE-B",
        quantity_used=5,  # Usage rate: 0.167 units/day
    )

    # LOT-2 at SITE-B: High usage (will run out soon)
    record_stock_usage(
        test_db,
        lot_number="LOT-2",
        site_name="SITE-B",
        quantity_used=40,  # Usage rate: 1.33 units/day
    )

    # LOT-2 at SITE-C: Low usage (surplus)
    record_stock_usage(
        test_db,
        lot_number="LOT-2",
        site_name="SITE-C",
        quantity_used=5,  # Usage rate: 0.167 units/day
    )

    # Get transfer suggestions
    suggestions = suggest_inventory_transfers(test_db)

    # Should suggest two transfers
    EXPECTED_TRANSFERS = 2
    assert len(suggestions) == EXPECTED_TRANSFERS

    # Sort suggestions by lot number for consistent testing
    suggestions = sorted(suggestions, key=lambda x: x.lot_number)

    # Check LOT-1 transfer
    assert suggestions[0].lot_number == "LOT-1"
    assert suggestions[0].source_site == "SITE-B"
    assert suggestions[0].destination_site == "SITE-A"
    assert suggestions[0].quantity > 0
    assert suggestions[0].days_extended > 0

    # Check LOT-2 transfer
    assert suggestions[1].lot_number == "LOT-2"
    assert suggestions[1].source_site == "SITE-C"
    assert suggestions[1].destination_site == "SITE-B"
    assert suggestions[1].quantity > 0
    assert suggestions[1].days_extended > 0


def test_suggest_inventory_transfers_no_surplus(test_db):
    """Test that no transfers are suggested when there's no surplus inventory."""
    # Create a lot and sites
    create_lot(
        test_db,
        lot_number="TEST-LOT-1",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=100,
    )
    create_site(test_db, site_name="SITE-A", contact_info="Test Contact A")
    create_site(test_db, site_name="SITE-B", contact_info="Test Contact B")

    # Create shipments to both sites, 30 days ago
    past_date = date.today() - timedelta(days=30)
    shipment_a = create_shipment(
        test_db,
        lot_number="TEST-LOT-1",
        site_name="SITE-A",
        shipment_date=past_date,
        quantity_shipped=50,
    )
    shipment_b = create_shipment(
        test_db,
        lot_number="TEST-LOT-1",
        site_name="SITE-B",
        shipment_date=past_date,
        quantity_shipped=50,
    )

    # Record arrivals
    record_stock_arrival(test_db, shipment_id=shipment_a.shipment_id)
    record_stock_arrival(test_db, shipment_id=shipment_b.shipment_id)

    # Both sites have high usage (neither has surplus)
    record_stock_usage(
        test_db,
        lot_number="TEST-LOT-1",
        site_name="SITE-A",
        quantity_used=40,
    )
    record_stock_usage(
        test_db,
        lot_number="TEST-LOT-1",
        site_name="SITE-B",
        quantity_used=40,
    )

    suggestions = suggest_inventory_transfers(test_db)
    assert len(suggestions) == 0
