# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
from datetime import date, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st
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


# Define a Hypothesis strategy for generating Lot data
lots_strategy = st.builds(
    Lot,
    lot_number=st.text(min_size=1, max_size=50),
    expiration_date=st.dates(
        min_value=date.today() + timedelta(days=1),
        max_value=date.today() + timedelta(days=365 * 5),
    ),
    initial_quantity=st.integers(min_value=0, max_value=10000),
)

# Define a Hypothesis strategy for generating Site data
sites_strategy = st.builds(
    Site,
    site_name=st.text(min_size=1, max_size=100),
    contact_info=st.text(min_size=0, max_size=200),
)


# Define a Hypothesis strategy for generating Shipment data
@st.composite
def shipments_strategy(draw):
    lot_data = draw(lots_strategy)
    site_data = draw(sites_strategy)

    # Ensure initial quantity is sufficient for shipment
    quantity_shipped = draw(st.integers(min_value=1, max_value=10000))
    lot_data.initial_quantity = quantity_shipped + draw(
        st.integers(min_value=0, max_value=1000)
    )

    shipment_specific_data = {
        "shipment_date": draw(
            st.dates(
                min_value=date.today() - timedelta(days=30),
                max_value=date.today() + timedelta(days=30),
            )
        ),
        "quantity_shipped": quantity_shipped,
        "anticipated_arrival_date": draw(
            st.dates(
                min_value=date.today(),
                max_value=date.today() + timedelta(days=60),
            )
        ),
    }
    return lot_data, site_data, shipment_specific_data


@given(lot_data=lots_strategy)
def test_property_create_lot(lot_data):
    """Test creating a lot record with property-based testing."""
    # Setup a new in-memory database for each test example
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = init_db("sqlite:///:memory:")
    session = session_factory()

    try:
        # Create a Lot object using the generated data
        lot = Lot(
            lot_number=lot_data.lot_number,
            expiration_date=lot_data.expiration_date,
            initial_quantity=lot_data.initial_quantity,
        )
        session.add(lot)
        session.commit()

        # Query the Lot back from the database
        result = session.query(Lot).filter_by(lot_number=lot_data.lot_number).first()

        # Assert that the retrieved Lot object is not None
        assert result is not None

        # Assert that its attributes match the generated values
        assert result.lot_number == lot_data.lot_number
        assert result.expiration_date == lot_data.expiration_date
        assert result.initial_quantity == lot_data.initial_quantity
    finally:
        session.close()


@given(shipment_creation_data=shipments_strategy())
def test_property_create_shipment(shipment_creation_data):
    """Test creating a shipment record with property-based testing."""
    lot_data, site_data, shipment_specific_data = shipment_creation_data

    # Setup a new in-memory database for each test example
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = init_db("sqlite:///:memory:")
    session = session_factory()

    try:
        # Create and persist Lot
        lot = Lot(
            lot_number=lot_data.lot_number,
            expiration_date=lot_data.expiration_date,
            initial_quantity=lot_data.initial_quantity,
        )
        session.add(lot)
        session.commit()
        # Refresh to get Lot with all fields populated if needed, e.g., lot_id
        session.refresh(lot)

        # Create and persist Site
        site = Site(
            site_name=site_data.site_name,
            contact_info=site_data.contact_info,
        )
        session.add(site)
        session.commit()
        # Refresh to get Site with all fields populated if needed, e.g., site_id
        session.refresh(site)

        # Create Shipment
        shipment = Shipment(
            lot_number=lot.lot_number,  # Use lot_number from persisted Lot
            site_name=site.site_name,  # Use site_name from persisted Site
            shipment_date=shipment_specific_data["shipment_date"],
            quantity_shipped=shipment_specific_data["quantity_shipped"],
            anticipated_arrival_date=shipment_specific_data["anticipated_arrival_date"],
        )
        session.add(shipment)
        session.commit()
        # Refresh to get Shipment with all fields populated, e.g., shipment_id
        session.refresh(shipment)

        # Query the Shipment back from the database
        # Using shipment_id is the most robust way if it's available
        retrieved_shipment = session.query(Shipment).get(shipment.shipment_id)

        # Assert that the retrieved Shipment object is not None
        assert retrieved_shipment is not None

        # Assert its properties match the generated/input data
        assert retrieved_shipment.lot_number == lot.lot_number
        assert retrieved_shipment.site_name == site.site_name
        assert (
            retrieved_shipment.shipment_date == shipment_specific_data["shipment_date"]
        )
        assert (
            retrieved_shipment.quantity_shipped
            == shipment_specific_data["quantity_shipped"]
        )
        assert (
            retrieved_shipment.anticipated_arrival_date
            == shipment_specific_data["anticipated_arrival_date"]
        )

        # Assert relationships
        assert retrieved_shipment.lot is not None
        assert retrieved_shipment.site is not None
        assert retrieved_shipment.lot.lot_number == lot.lot_number
        assert retrieved_shipment.site.site_name == site.site_name

    finally:
        session.close()


# Define a Hypothesis strategy for generating Inventory data
@st.composite
def inventories_strategy(draw):
    lot_data = draw(lots_strategy)
    site_data = draw(sites_strategy)
    inventory_specific_data = {
        "current_quantity": draw(st.integers(min_value=0, max_value=100000)),
        "last_updated_date": draw(
            st.dates(
                min_value=date.today() - timedelta(days=30),
                max_value=date.today(),
            )
        ),
    }
    return lot_data, site_data, inventory_specific_data


@given(site_data=sites_strategy)
def test_property_create_site(site_data):
    """Test creating a site record with property-based testing."""
    # Setup a new in-memory database for each test example
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = init_db("sqlite:///:memory:")
    session = session_factory()

    try:
        # Create a Site object using the generated data
        site = Site(
            site_name=site_data.site_name,
            contact_info=site_data.contact_info,
        )
        session.add(site)
        session.commit()

        # Query the Site back from the database
        result = session.query(Site).filter_by(site_name=site_data.site_name).first()

        # Assert that the retrieved Site object is not None
        assert result is not None

        # Assert that its attributes match the generated values
        assert result.site_name == site_data.site_name
        assert result.contact_info == site_data.contact_info
    finally:
        session.close()


@given(inventory_creation_data=inventories_strategy())
def test_property_create_inventory(inventory_creation_data):
    """Test creating an inventory record with property-based testing."""
    lot_data, site_data, inventory_specific_data = inventory_creation_data

    # Setup a new in-memory database for each test example
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = init_db("sqlite:///:memory:")
    session = session_factory()

    try:
        # Create and persist Lot
        lot = Lot(
            lot_number=lot_data.lot_number,
            expiration_date=lot_data.expiration_date,
            initial_quantity=lot_data.initial_quantity,
        )
        session.add(lot)
        session.commit()
        session.refresh(lot)

        # Create and persist Site
        site = Site(
            site_name=site_data.site_name,
            contact_info=site_data.contact_info,
        )
        session.add(site)
        session.commit()
        session.refresh(site)

        # Create Inventory
        inventory = Inventory(
            lot_number=lot.lot_number,
            site_name=site.site_name,
            current_quantity=inventory_specific_data["current_quantity"],
            last_updated_date=inventory_specific_data["last_updated_date"],
        )
        session.add(inventory)
        session.commit()
        session.refresh(inventory)

        # Query the Inventory back from the database
        retrieved_inventory = session.query(Inventory).get(inventory.inventory_id)

        # Assert that the retrieved Inventory object is not None
        assert retrieved_inventory is not None

        # Assert its properties match the generated/input data
        assert (
            retrieved_inventory.current_quantity
            == inventory_specific_data["current_quantity"]
        )
        assert (
            retrieved_inventory.last_updated_date
            == inventory_specific_data["last_updated_date"]
        )

        # Assert relationships
        assert retrieved_inventory.lot is not None
        assert retrieved_inventory.site is not None
        assert retrieved_inventory.lot.lot_number == lot.lot_number
        assert retrieved_inventory.site.site_name == site.site_name

    finally:
        session.close()
