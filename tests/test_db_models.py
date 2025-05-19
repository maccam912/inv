# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine

from inv.db.models import Base, Inventory, Lot, Shipment, Site, init_db

# Constants for testing
INITIAL_LOT_QUANTITY = 100
INITIAL_INVENTORY_QUANTITY = 150


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    session_factory = init_db("sqlite:///:memory:")
    session = session_factory()

    yield session

    session.close()


def test_create_lot(test_db):
    """Test creating a lot record."""
    lot = Lot(
        lot_number="LOT123",
        expiration_date=date.today() + timedelta(days=365),
        initial_quantity=INITIAL_LOT_QUANTITY,
    )
    test_db.add(lot)
    test_db.commit()

    result = test_db.query(Lot).filter_by(lot_number="LOT123").first()
    assert result is not None
    assert result.lot_number == "LOT123"
    assert result.initial_quantity == INITIAL_LOT_QUANTITY


def test_create_site(test_db):
    """Test creating a site record."""
    site = Site(site_name="Warehouse A", contact_info="John Doe, 555-1234")
    test_db.add(site)
    test_db.commit()

    result = test_db.query(Site).filter_by(site_name="Warehouse A").first()
    assert result is not None
    assert result.site_name == "Warehouse A"
    assert result.contact_info == "John Doe, 555-1234"


def test_create_shipment_and_relationships(test_db):
    """Test creating a shipment with relationships to lot and site."""
    # Create a lot and site first
    lot = Lot(
        lot_number="LOT456",
        expiration_date=date.today() + timedelta(days=180),
        initial_quantity=50,
    )
    site = Site(site_name="Store B", contact_info="Jane Smith, 555-5678")
    test_db.add_all([lot, site])
    test_db.commit()

    # Create a shipment connected to the lot and site
    shipment = Shipment(
        lot_number="LOT456",
        site_name="Store B",
        shipment_date=date.today(),
        quantity_shipped=25,
        anticipated_arrival_date=date.today() + timedelta(days=3),
    )
    test_db.add(shipment)
    test_db.commit()

    # Test the shipment
    result = test_db.query(Shipment).first()
    assert result is not None
    assert result.lot_number == "LOT456"
    assert result.site_name == "Store B"

    # Test relationships
    assert result.lot.lot_number == "LOT456"
    assert result.site.site_name == "Store B"

    # Test reverse relationships
    assert len(lot.shipments) == 1
    assert lot.shipments[0].shipment_id == result.shipment_id
    assert len(site.shipments) == 1
    assert site.shipments[0].shipment_id == result.shipment_id


def test_create_inventory(test_db):
    """Test creating an inventory record with relationships to lot and site."""
    # Create a lot and site first
    lot = Lot(
        lot_number="LOT789",
        expiration_date=date.today() + timedelta(days=90),
        initial_quantity=200,
    )
    site = Site(
        site_name="Distribution Center", contact_info="Operations Team, 555-9876"
    )
    test_db.add_all([lot, site])
    test_db.commit()

    # Create inventory for the lot at the site
    inventory = Inventory(
        lot_number="LOT789",
        site_name="Distribution Center",
        current_quantity=INITIAL_INVENTORY_QUANTITY,
        last_updated_date=date.today(),
    )
    test_db.add(inventory)
    test_db.commit()

    # Test the inventory
    result = test_db.query(Inventory).first()
    assert result is not None
    assert result.lot_number == "LOT789"
    assert result.site_name == "Distribution Center"
    assert result.current_quantity == INITIAL_INVENTORY_QUANTITY

    # Test relationships
    assert result.lot.lot_number == "LOT789"
    assert result.site.site_name == "Distribution Center"

    # Test reverse relationships
    assert len(lot.inventory) == 1
    assert lot.inventory[0].inventory_id == result.inventory_id
    assert len(site.inventory) == 1
    assert site.inventory[0].inventory_id == result.inventory_id
