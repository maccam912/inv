# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for lot database operations."""

from datetime import date, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from inv.db.models import Lot, init_db
from inv.db.operations import (
    create_lot,
    delete_lot,
    read_lot,
    read_lots,
    update_lot,
)

# Constants for testing
INITIAL_LOT_QUANTITY = 100
# Constants for test_read_lots
EXPECTED_TOTAL_LOTS = 4
EXPECTED_EXPIRED_LOTS = 2
EXPECTED_NON_EXPIRED_LOTS = 2
EXPECTED_BEFORE_DATE_LOTS = 3
EXPECTED_AFTER_DATE_LOTS = 3


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    session_factory = init_db("sqlite:///:memory:")
    session = session_factory()

    yield session

    session.close()


def test_create_lot(test_db):
    """Test creating a lot record using the create_lot function."""
    expiration_date = date.today() + timedelta(days=365)
    lot = create_lot(
        test_db,
        lot_number="LOT123",
        expiration_date=expiration_date,
        initial_quantity=INITIAL_LOT_QUANTITY,
    )

    assert lot is not None
    assert lot.lot_number == "LOT123"
    assert lot.expiration_date == expiration_date
    assert lot.initial_quantity == INITIAL_LOT_QUANTITY

    # Verify it was added to the database
    result = test_db.query(Lot).filter_by(lot_number="LOT123").first()
    assert result is not None
    assert result.lot_number == "LOT123"
    assert result.initial_quantity == INITIAL_LOT_QUANTITY


def test_create_duplicate_lot(test_db):
    """Test that creating a lot with a duplicate lot number raises IntegrityError."""
    # Create first lot
    create_lot(
        test_db,
        lot_number="LOT123",
        expiration_date=date.today() + timedelta(days=365),
        initial_quantity=INITIAL_LOT_QUANTITY,
    )

    # Attempt to create a lot with the same lot number should raise IntegrityError
    with pytest.raises(IntegrityError):
        create_lot(
            test_db,
            lot_number="LOT123",
            expiration_date=date.today() + timedelta(days=180),
            initial_quantity=200,
        )


def test_read_lot(test_db):
    """Test reading a lot record by lot number."""
    # Create a lot first
    expiration_date = date.today() + timedelta(days=365)
    create_lot(
        test_db,
        lot_number="LOT456",
        expiration_date=expiration_date,
        initial_quantity=INITIAL_LOT_QUANTITY,
    )

    # Read the lot
    lot = read_lot(test_db, lot_number="LOT456")
    assert lot is not None
    assert lot.lot_number == "LOT456"
    assert lot.expiration_date == expiration_date
    assert lot.initial_quantity == INITIAL_LOT_QUANTITY


def test_read_lot_not_found(test_db):
    """Test reading a non-existent lot returns None."""
    lot = read_lot(test_db, lot_number="NONEXISTENT")
    assert lot is None


def test_read_lots(test_db):
    """Test reading multiple lots."""
    today = date.today()

    # Create several lots with different expiration dates
    create_lot(
        test_db,
        lot_number="LOT_EXPIRED1",
        expiration_date=today - timedelta(days=10),
        initial_quantity=50,
    )
    create_lot(
        test_db,
        lot_number="LOT_EXPIRED2",
        expiration_date=today - timedelta(days=5),
        initial_quantity=60,
    )
    create_lot(
        test_db,
        lot_number="LOT_FUTURE1",
        expiration_date=today + timedelta(days=30),
        initial_quantity=70,
    )
    create_lot(
        test_db,
        lot_number="LOT_FUTURE2",
        expiration_date=today + timedelta(days=60),
        initial_quantity=80,
    )

    # Test reading all lots
    all_lots = read_lots(test_db)
    # We expect 4 lots based on the test setup
    assert len(all_lots) == EXPECTED_TOTAL_LOTS

    # Test reading expired lots
    expired_lots = read_lots(test_db, expired=True)
    # We expect 2 expired lots based on the test setup
    assert len(expired_lots) == EXPECTED_EXPIRED_LOTS
    assert all(lot.expiration_date < today for lot in expired_lots)

    # Test reading non-expired lots
    non_expired_lots = read_lots(test_db, expired=False)
    # We expect 2 non-expired lots based on the test setup
    assert len(non_expired_lots) == EXPECTED_NON_EXPIRED_LOTS
    assert all(lot.expiration_date >= today for lot in non_expired_lots)

    # Test reading lots expiring before a certain date
    before_lots = read_lots(test_db, expiration_before=today + timedelta(days=40))
    # We expect 3 lots expiring before today+40 days based on the test setup
    assert len(before_lots) == EXPECTED_BEFORE_DATE_LOTS
    assert all(lot.expiration_date < today + timedelta(days=40) for lot in before_lots)

    # Test reading lots expiring after a certain date
    after_lots = read_lots(test_db, expiration_after=today - timedelta(days=7))
    # We expect 3 lots expiring after today-7 days based on the test setup
    assert len(after_lots) == EXPECTED_AFTER_DATE_LOTS
    assert all(lot.expiration_date > today - timedelta(days=7) for lot in after_lots)

    # Test combined filters
    combined_lots = read_lots(
        test_db, expired=False, expiration_before=today + timedelta(days=40)
    )
    assert len(combined_lots) == 1
    assert combined_lots[0].lot_number == "LOT_FUTURE1"


def test_update_lot(test_db):
    """Test updating a lot record."""
    original_date = date.today() + timedelta(days=365)
    create_lot(
        test_db,
        lot_number="LOT789",
        expiration_date=original_date,
        initial_quantity=INITIAL_LOT_QUANTITY,
    )

    # Update the lot
    new_date = date.today() + timedelta(days=180)
    new_quantity = 200
    updated_lot = update_lot(
        test_db,
        lot_number="LOT789",
        expiration_date=new_date,
        initial_quantity=new_quantity,
    )

    assert updated_lot is not None
    assert updated_lot.lot_number == "LOT789"
    assert updated_lot.expiration_date == new_date
    assert updated_lot.initial_quantity == new_quantity

    # Verify in database
    result = test_db.query(Lot).filter_by(lot_number="LOT789").first()
    assert result is not None
    assert result.expiration_date == new_date
    assert result.initial_quantity == new_quantity


def test_update_lot_partial(test_db):
    """Test partial update of a lot record."""
    original_date = date.today() + timedelta(days=365)
    original_quantity = 150
    create_lot(
        test_db,
        lot_number="LOT789",
        expiration_date=original_date,
        initial_quantity=original_quantity,
    )

    # Update only the expiration date
    new_date = date.today() + timedelta(days=180)
    updated_lot = update_lot(
        test_db,
        lot_number="LOT789",
        expiration_date=new_date,
    )

    assert updated_lot.expiration_date == new_date
    assert updated_lot.initial_quantity == original_quantity

    # Update only the quantity
    new_quantity = 200
    updated_lot = update_lot(
        test_db,
        lot_number="LOT789",
        initial_quantity=new_quantity,
    )

    assert updated_lot.expiration_date == new_date
    assert updated_lot.initial_quantity == new_quantity


def test_update_lot_not_found(test_db):
    """Test updating a non-existent lot returns None."""
    result = update_lot(
        test_db,
        lot_number="NONEXISTENT",
        expiration_date=date.today(),
        initial_quantity=100,
    )
    assert result is None


def test_delete_lot(test_db):
    """Test deleting a lot record."""
    # Create a lot
    create_lot(
        test_db,
        lot_number="LOT999",
        expiration_date=date.today() + timedelta(days=30),
        initial_quantity=75,
    )

    # Verify it exists
    assert read_lot(test_db, "LOT999") is not None

    # Delete the lot
    result = delete_lot(test_db, "LOT999")
    assert result is True

    # Verify it's gone
    assert read_lot(test_db, "LOT999") is None


def test_delete_lot_not_found(test_db):
    """Test deleting a non-existent lot returns False."""
    result = delete_lot(test_db, "NONEXISTENT")
    assert result is False
