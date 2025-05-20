# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Operations for managing lots and sites in the database."""

from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from inv.db.models import Lot, Site


def create_lot(
    session: Session, lot_number: str, expiration_date: date, initial_quantity: int
) -> Lot:
    """
    Create a new lot in the database.

    Args:
        session: Database session
        lot_number: Unique identifier for the lot
        expiration_date: Date when the lot will expire
        initial_quantity: The original quantity of items in the lot

    Returns:
        The created lot object

    Raises:
        IntegrityError: If a lot with the same lot number already exists
    """
    lot = Lot(
        lot_number=lot_number,
        expiration_date=expiration_date,
        initial_quantity=initial_quantity,
    )
    session.add(lot)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    return lot


def read_lot(session: Session, lot_number: str) -> Lot | None:
    """
    Read a lot from the database by its lot number.

    Args:
        session: Database session
        lot_number: Unique identifier for the lot

    Returns:
        The lot object if found, None otherwise
    """
    return session.query(Lot).filter_by(lot_number=lot_number).first()


def read_lots(
    session: Session,
    expired: bool | None = None,
    expiration_before: date | None = None,
    expiration_after: date | None = None,
) -> list[Lot]:
    """
    Read lots from the database with optional filtering.

    Args:
        session: Database session
        expired: If True, only return expired lots; if False, only return non-expired lots
        expiration_before: Only return lots expiring before this date
        expiration_after: Only return lots expiring after this date

    Returns:
        A list of lot objects matching the criteria
    """
    query = session.query(Lot)

    # Apply filters if provided
    if expired is not None:
        if expired:
            query = query.filter(Lot.expiration_date < date.today())
        else:
            query = query.filter(Lot.expiration_date >= date.today())

    if expiration_before is not None:
        query = query.filter(Lot.expiration_date < expiration_before)

    if expiration_after is not None:
        query = query.filter(Lot.expiration_date > expiration_after)

    return query.all()


def update_lot(
    session: Session,
    lot_number: str,
    expiration_date: date | None = None,
    initial_quantity: int | None = None,
) -> Lot | None:
    """
    Update a lot in the database.

    Args:
        session: Database session
        lot_number: Unique identifier for the lot
        expiration_date: New expiration date (if None, not updated)
        initial_quantity: New initial quantity (if None, not updated)

    Returns:
        The updated lot object if found, None otherwise

    Raises:
        IntegrityError: If the update violates database constraints
    """
    lot = read_lot(session, lot_number)
    if lot is None:
        return None

    if expiration_date is not None:
        lot.expiration_date = expiration_date
    if initial_quantity is not None:
        lot.initial_quantity = initial_quantity

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise

    return lot


def delete_lot(session: Session, lot_number: str) -> bool:
    """
    Delete a lot from the database.

    Args:
        session: Database session
        lot_number: Unique identifier for the lot to delete

    Returns:
        True if the lot was deleted, False if not found

    Raises:
        IntegrityError: If the deletion would violate foreign key constraints
                        (e.g., if there are related shipments or inventory records)
    """
    lot = read_lot(session, lot_number)
    if lot is None:
        return False

    try:
        session.delete(lot)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise

    return True


def create_site(
    session: Session, site_name: str, contact_info: str | None = None
) -> Site:
    """
    Create a new site in the database.

    Args:
        session: Database session
        site_name: Unique identifier for the site
        contact_info: Contact information for the site

    Returns:
        The created site object

    Raises:
        IntegrityError: If a site with the same site name already exists
    """
    site = Site(site_name=site_name, contact_info=contact_info)
    session.add(site)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    return site


def read_site(session: Session, site_name: str) -> Site | None:
    """
    Read a site from the database by its site name.

    Args:
        session: Database session
        site_name: Unique identifier for the site

    Returns:
        The site object if found, None otherwise
    """
    return session.query(Site).filter_by(site_name=site_name).first()


def read_sites(session: Session) -> list[Site]:
    """
    Read all sites from the database.

    Args:
        session: Database session

    Returns:
        A list of all site objects
    """
    return session.query(Site).all()


def update_site(
    session: Session, site_name: str, contact_info: str | None = None
) -> Site | None:
    """
    Update a site in the database.

    Args:
        session: Database session
        site_name: Unique identifier for the site
        contact_info: New contact information (if None, not updated)

    Returns:
        The updated site object if found, None otherwise

    Raises:
        IntegrityError: If the update violates database constraints
    """
    site = read_site(session, site_name)
    if site is None:
        return None

    if contact_info is not None:
        site.contact_info = contact_info

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise

    return site


def delete_site(session: Session, site_name: str) -> bool:
    """
    Delete a site from the database.

    Args:
        session: Database session
        site_name: Unique identifier for the site to delete

    Returns:
        True if the site was deleted, False if not found

    Raises:
        IntegrityError: If the deletion would violate foreign key constraints
                        (e.g., if there are related shipments or inventory records)
    """
    site = read_site(session, site_name)
    if site is None:
        return False

    try:
        session.delete(site)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise

    return True
