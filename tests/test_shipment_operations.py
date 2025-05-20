# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for shipment database operations."""

from datetime import date, timedelta

import pytest

from inv.db.models import Lot, Shipment, Site, init_db
from inv.db.operations import (
    create_lot,
    create_shipment,
    create_site,
    delete_shipment,
    read_shipment,
    read_shipments,
    update_shipment,
)

# Constants for testing
EXPECTED_TOTAL_SHIPMENTS = 3
EXPECTED_LOT_B_SHIPMENTS = 2
EXPECTED_SITE_Z_SHIPMENTS = 2
TEST_SHIPMENT_QUANTITY = 25
UPDATED_SHIPMENT_QUANTITY = 30


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    session_factory = init_db("sqlite:///:memory:")
    session = session_factory()

    yield session

    session.close()


@pytest.fixture
def test_lot_and_site(test_db):
    """Create a test lot and site for shipment tests."""
    # Create a lot and site that will be used by shipment tests
    lot = create_lot(
        test_db,
        lot_number="LOT456",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=50,
    )
    site = create_site(
        test_db,
        site_name="Store B",
        contact_info="Jane Smith, 555-5678",
    )
    return lot, site


def test_create_shipment(test_db, test_lot_and_site):
    """Test creating a shipment record using the create_shipment function."""
    shipment_date = date.today()
    arrival_date = shipment_date + timedelta(days=3)

    shipment = create_shipment(
        test_db,
        lot_number="LOT456",
        site_name="Store B",
        shipment_date=shipment_date,
        quantity_shipped=TEST_SHIPMENT_QUANTITY,
        anticipated_arrival_date=arrival_date,
    )

    assert shipment is not None
    assert shipment.lot_number == "LOT456"
    assert shipment.site_name == "Store B"
    assert shipment.shipment_date == shipment_date
    assert shipment.quantity_shipped == TEST_SHIPMENT_QUANTITY
    assert shipment.anticipated_arrival_date == arrival_date

    # Verify it was added to the database
    result = test_db.query(Shipment).filter_by(shipment_id=shipment.shipment_id).first()
    assert result is not None
    assert result.lot_number == "LOT456"
    assert result.site_name == "Store B"
    assert result.shipment_date == shipment_date
    assert result.quantity_shipped == TEST_SHIPMENT_QUANTITY
    assert result.anticipated_arrival_date == arrival_date


def test_create_shipment_without_arrival_date(test_db, test_lot_and_site):
    """Test creating a shipment record without an arrival date."""
    shipment_date = date.today()

    shipment = create_shipment(
        test_db,
        lot_number="LOT456",
        site_name="Store B",
        shipment_date=shipment_date,
        quantity_shipped=TEST_SHIPMENT_QUANTITY,
    )

    assert shipment is not None
    assert shipment.lot_number == "LOT456"
    assert shipment.site_name == "Store B"
    assert shipment.shipment_date == shipment_date
    assert shipment.quantity_shipped == TEST_SHIPMENT_QUANTITY
    assert shipment.anticipated_arrival_date is None

    # Verify it was added to the database
    result = test_db.query(Shipment).filter_by(shipment_id=shipment.shipment_id).first()
    assert result is not None
    assert result.anticipated_arrival_date is None


def test_create_shipment_relationships(test_db, test_lot_and_site):
    """Test that the shipment properly relates to lot and site records."""
    lot, site = test_lot_and_site

    shipment = create_shipment(
        test_db,
        lot_number="LOT456",
        site_name="Store B",
        shipment_date=date.today(),
        quantity_shipped=25,
    )

    # Test relationships
    assert shipment.lot.lot_number == "LOT456"
    assert shipment.site.site_name == "Store B"

    # Test reverse relationships
    lot_from_db = test_db.query(Lot).filter_by(lot_number="LOT456").first()
    assert len(lot_from_db.shipments) == 1
    assert lot_from_db.shipments[0].shipment_id == shipment.shipment_id

    site_from_db = test_db.query(Site).filter_by(site_name="Store B").first()
    assert len(site_from_db.shipments) == 1
    assert site_from_db.shipments[0].shipment_id == shipment.shipment_id


def test_read_shipment(test_db, test_lot_and_site):
    """Test reading a shipment record by shipment ID."""
    # Create a shipment first
    shipment = create_shipment(
        test_db,
        lot_number="LOT456",
        site_name="Store B",
        shipment_date=date.today(),
        quantity_shipped=25,
    )

    # Read the shipment
    result = read_shipment(test_db, shipment.shipment_id)
    assert result is not None
    assert result.shipment_id == shipment.shipment_id
    assert result.lot_number == "LOT456"
    assert result.site_name == "Store B"


def test_read_shipment_not_found(test_db):
    """Test reading a non-existent shipment returns None."""
    result = read_shipment(test_db, 999)  # Non-existent ID
    assert result is None


def test_read_shipments(test_db, test_lot_and_site):
    """Test reading all shipment records."""
    # Create several shipments
    create_shipment(test_db, lot_number="LOT456", site_name="Store B",
                    shipment_date=date.today(), quantity_shipped=10)
    create_shipment(test_db, lot_number="LOT456", site_name="Store B",
                    shipment_date=date.today() + timedelta(days=1), quantity_shipped=15)
    create_shipment(test_db, lot_number="LOT456", site_name="Store B",
                    shipment_date=date.today() + timedelta(days=2), quantity_shipped=20)

    # Read all shipments
    shipments = read_shipments(test_db)
    assert len(shipments) == EXPECTED_TOTAL_SHIPMENTS


def test_read_shipments_by_lot(test_db):
    """Test reading shipments filtered by lot number."""
    # Create lots and site first
    create_lot(test_db, lot_number="LOT-A", expiration_date=date.today() + timedelta(days=180), initial_quantity=100)
    create_lot(test_db, lot_number="LOT-B", expiration_date=date.today() + timedelta(days=180), initial_quantity=100)
    create_site(test_db, site_name="Site-X", contact_info="Contact X")

    # Create shipments for different lots
    create_shipment(test_db, lot_number="LOT-A", site_name="Site-X",
                    shipment_date=date.today(), quantity_shipped=10)
    create_shipment(test_db, lot_number="LOT-B", site_name="Site-X",
                    shipment_date=date.today(), quantity_shipped=20)
    create_shipment(test_db, lot_number="LOT-B", site_name="Site-X",
                    shipment_date=date.today() + timedelta(days=1), quantity_shipped=30)

    # Read shipments by lot
    lot_a_shipments = read_shipments(test_db, lot_number="LOT-A")
    assert len(lot_a_shipments) == 1
    assert lot_a_shipments[0].lot_number == "LOT-A"

    lot_b_shipments = read_shipments(test_db, lot_number="LOT-B")
    assert len(lot_b_shipments) == EXPECTED_LOT_B_SHIPMENTS
    assert all(s.lot_number == "LOT-B" for s in lot_b_shipments)


def test_read_shipments_by_site(test_db):
    """Test reading shipments filtered by site name."""
    # Create lot and sites first
    create_lot(test_db, lot_number="LOT-C", expiration_date=date.today() + timedelta(days=180), initial_quantity=100)
    create_site(test_db, site_name="Site-Y", contact_info="Contact Y")
    create_site(test_db, site_name="Site-Z", contact_info="Contact Z")

    # Create shipments for different sites
    create_shipment(test_db, lot_number="LOT-C", site_name="Site-Y",
                    shipment_date=date.today(), quantity_shipped=10)
    create_shipment(test_db, lot_number="LOT-C", site_name="Site-Z",
                    shipment_date=date.today(), quantity_shipped=20)
    create_shipment(test_db, lot_number="LOT-C", site_name="Site-Z",
                    shipment_date=date.today() + timedelta(days=1), quantity_shipped=30)

    # Read shipments by site
    site_y_shipments = read_shipments(test_db, site_name="Site-Y")
    assert len(site_y_shipments) == 1
    assert site_y_shipments[0].site_name == "Site-Y"

    site_z_shipments = read_shipments(test_db, site_name="Site-Z")
    assert len(site_z_shipments) == EXPECTED_SITE_Z_SHIPMENTS
    assert all(s.site_name == "Site-Z" for s in site_z_shipments)


def test_update_shipment(test_db, test_lot_and_site):
    """Test updating a shipment record."""
    # Create another lot and site for testing updates
    create_lot(test_db, lot_number="LOT789", expiration_date=date.today() + timedelta(days=180), initial_quantity=100)
    create_site(test_db, site_name="Store C", contact_info="New Contact")

    # Create a shipment first
    original_date = date.today()
    shipment = create_shipment(
        test_db,
        lot_number="LOT456",
        site_name="Store B",
        shipment_date=original_date,
        quantity_shipped=25,
    )

    # Update the shipment
    new_date = date.today() + timedelta(days=5)
    new_arrival_date = date.today() + timedelta(days=7)
    updated_shipment = update_shipment(
        test_db,
        shipment_id=shipment.shipment_id,
        lot_number="LOT789",
        site_name="Store C",
        shipment_date=new_date,
        quantity_shipped=UPDATED_SHIPMENT_QUANTITY,
        anticipated_arrival_date=new_arrival_date,
    )

    assert updated_shipment is not None
    assert updated_shipment.shipment_id == shipment.shipment_id
    assert updated_shipment.lot_number == "LOT789"
    assert updated_shipment.site_name == "Store C"
    assert updated_shipment.shipment_date == new_date
    assert updated_shipment.quantity_shipped == UPDATED_SHIPMENT_QUANTITY
    assert updated_shipment.anticipated_arrival_date == new_arrival_date

    # Verify in database
    result = test_db.query(Shipment).filter_by(shipment_id=shipment.shipment_id).first()
    assert result is not None
    assert result.lot_number == "LOT789"
    assert result.site_name == "Store C"
    assert result.shipment_date == new_date
    assert result.quantity_shipped == UPDATED_SHIPMENT_QUANTITY
    assert result.anticipated_arrival_date == new_arrival_date


def test_update_shipment_partial(test_db, test_lot_and_site):
    """Test partial update of a shipment record."""
    # Create a shipment first
    original_date = date.today()
    original_quantity = 25
    shipment = create_shipment(
        test_db,
        lot_number="LOT456",
        site_name="Store B",
        shipment_date=original_date,
        quantity_shipped=original_quantity,
    )

    # Update only the quantity
    new_quantity = 35
    updated_shipment = update_shipment(
        test_db,
        shipment_id=shipment.shipment_id,
        quantity_shipped=new_quantity,
    )

    assert updated_shipment is not None
    assert updated_shipment.lot_number == "LOT456"  # Unchanged
    assert updated_shipment.site_name == "Store B"  # Unchanged
    assert updated_shipment.shipment_date == original_date  # Unchanged
    assert updated_shipment.quantity_shipped == new_quantity  # Changed
    assert updated_shipment.anticipated_arrival_date is None  # Unchanged

    # Update only the anticipated arrival date
    new_arrival_date = date.today() + timedelta(days=10)
    updated_shipment = update_shipment(
        test_db,
        shipment_id=shipment.shipment_id,
        anticipated_arrival_date=new_arrival_date,
    )

    assert updated_shipment.anticipated_arrival_date == new_arrival_date  # Changed
    assert updated_shipment.quantity_shipped == new_quantity  # Unchanged
    assert updated_shipment.lot_number == "LOT456"  # Unchanged


def test_update_shipment_not_found(test_db):
    """Test updating a non-existent shipment returns None."""
    result = update_shipment(
        test_db,
        shipment_id=999,  # Non-existent ID
        quantity_shipped=50,
    )
    assert result is None


def test_delete_shipment(test_db, test_lot_and_site):
    """Test deleting a shipment record."""
    # Create a shipment
    shipment = create_shipment(
        test_db,
        lot_number="LOT456",
        site_name="Store B",
        shipment_date=date.today(),
        quantity_shipped=40,
    )

    # Verify it exists
    assert read_shipment(test_db, shipment.shipment_id) is not None

    # Delete the shipment
    result = delete_shipment(test_db, shipment.shipment_id)
    assert result is True

    # Verify it's gone
    assert read_shipment(test_db, shipment.shipment_id) is None


def test_delete_shipment_not_found(test_db):
    """Test deleting a non-existent shipment returns False."""
    result = delete_shipment(test_db, 999)  # Non-existent ID
    assert result is False
