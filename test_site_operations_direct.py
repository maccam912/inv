"""Simple direct test for site operations."""

import os
import sys

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath("."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from inv.db.models import Base
from inv.db.operations import (
    create_site,
    delete_site,
    read_site,
    read_sites,
    update_site,
)


def main():
    """Run direct tests for site operations."""
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Testing site operations...")

    # Create site
    site = create_site(session, "Test Site", "Test Contact")
    print(f"Created site: {site.site_name}, Contact: {site.contact_info}")

    # Read site
    site = read_site(session, "Test Site")
    print(f"Read site: {site.site_name}, Contact: {site.contact_info}")

    # Update site
    updated_site = update_site(session, "Test Site", "Updated Contact")
    print(f"Updated site: {updated_site.site_name}, Contact: {updated_site.contact_info}")

    # Create another site
    create_site(session, "Another Site", "Another Contact")

    # Read all sites
    sites = read_sites(session)
    print(f"Total sites: {len(sites)}")
    for site in sites:
        print(f"- {site.site_name}: {site.contact_info}")

    # Delete site
    result = delete_site(session, "Test Site")
    print(f"Delete site result: {result}")

    # Verify deletion
    remaining_sites = read_sites(session)
    print(f"Remaining sites: {len(remaining_sites)}")
    for site in remaining_sites:
        print(f"- {site.site_name}: {site.contact_info}")

    print("All tests completed!")


if __name__ == "__main__":
    main()
