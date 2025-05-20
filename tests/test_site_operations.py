# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for site database operations."""

import pytest
from sqlalchemy.exc import IntegrityError

from inv.db.models import Site, init_db
from inv.db.operations import (
    create_site,
    delete_site,
    read_site,
    read_sites,
    update_site,
)


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    session_factory = init_db("sqlite:///:memory:")
    session = session_factory()

    yield session

    session.close()


def test_create_site(test_db):
    """Test creating a site record using the create_site function."""
    site = create_site(
        test_db,
        site_name="Warehouse A",
        contact_info="John Doe, 555-1234",
    )

    assert site is not None
    assert site.site_name == "Warehouse A"
    assert site.contact_info == "John Doe, 555-1234"

    # Verify it was added to the database
    result = test_db.query(Site).filter_by(site_name="Warehouse A").first()
    assert result is not None
    assert result.site_name == "Warehouse A"
    assert result.contact_info == "John Doe, 555-1234"


def test_create_site_without_contact_info(test_db):
    """Test creating a site record without contact info."""
    site = create_site(test_db, site_name="Warehouse B")

    assert site is not None
    assert site.site_name == "Warehouse B"
    assert site.contact_info is None

    # Verify it was added to the database
    result = test_db.query(Site).filter_by(site_name="Warehouse B").first()
    assert result is not None
    assert result.site_name == "Warehouse B"
    assert result.contact_info is None


def test_create_duplicate_site(test_db):
    """Test that creating a site with a duplicate site name raises IntegrityError."""
    # Create first site
    create_site(
        test_db,
        site_name="Warehouse C",
        contact_info="Jane Smith, 555-5678",
    )

    # Attempt to create a site with the same site name should raise IntegrityError
    with pytest.raises(IntegrityError):
        create_site(
            test_db,
            site_name="Warehouse C",
            contact_info="Different Contact, 555-9876",
        )


def test_read_site(test_db):
    """Test reading a site record by site name."""
    # Create a site first
    create_site(
        test_db,
        site_name="Warehouse D",
        contact_info="John Smith, 555-4321",
    )

    # Read the site
    site = read_site(test_db, "Warehouse D")
    assert site is not None
    assert site.site_name == "Warehouse D"
    assert site.contact_info == "John Smith, 555-4321"

    # Test reading a non-existent site
    site = read_site(test_db, "Nonexistent Warehouse")
    assert site is None


def test_read_sites(test_db):
    """Test reading all site records."""
    # Create several sites
    create_site(test_db, site_name="Warehouse E", contact_info="Contact E")
    create_site(test_db, site_name="Warehouse F", contact_info="Contact F")
    create_site(test_db, site_name="Warehouse G", contact_info="Contact G")

    # Read all sites
    sites = read_sites(test_db)
    assert len(sites) == 3  # noqa: PLR2004
    site_names = [site.site_name for site in sites]
    assert "Warehouse E" in site_names
    assert "Warehouse F" in site_names
    assert "Warehouse G" in site_names


def test_update_site(test_db):
    """Test updating a site record."""
    # Create a site first
    create_site(
        test_db,
        site_name="Warehouse H",
        contact_info="Original Contact",
    )

    # Update the site
    new_contact_info = "Updated Contact, 555-8765"
    updated_site = update_site(
        test_db,
        site_name="Warehouse H",
        contact_info=new_contact_info,
    )

    assert updated_site is not None
    assert updated_site.site_name == "Warehouse H"
    assert updated_site.contact_info == new_contact_info

    # Verify in database
    result = test_db.query(Site).filter_by(site_name="Warehouse H").first()
    assert result is not None
    assert result.contact_info == new_contact_info


def test_update_site_not_found(test_db):
    """Test updating a non-existent site returns None."""
    result = update_site(
        test_db,
        site_name="NONEXISTENT",
        contact_info="Some Contact",
    )
    assert result is None


def test_delete_site(test_db):
    """Test deleting a site record."""
    # Create a site
    create_site(
        test_db,
        site_name="Warehouse I",
        contact_info="Contact I",
    )

    # Verify it exists
    assert read_site(test_db, "Warehouse I") is not None

    # Delete the site
    result = delete_site(test_db, "Warehouse I")
    assert result is True

    # Verify it's gone
    assert read_site(test_db, "Warehouse I") is None


def test_delete_site_not_found(test_db):
    """Test deleting a non-existent site returns False."""
    result = delete_site(test_db, "NONEXISTENT")
    assert result is False