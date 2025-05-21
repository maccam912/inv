# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Operations for managing lots and sites in the database."""

from datetime import date, timedelta
from typing import NamedTuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from inv.db.models import Inventory, Lot, Shipment, Site


class TransferSuggestion(NamedTuple):
    """
    Represents a suggested inventory transfer between sites.

    Attributes:
        lot_number: The lot to be transferred
        source_site: Site with surplus inventory to send
        destination_site: Site running low on inventory
        quantity: Suggested quantity to transfer
        days_extended: Estimated days the transfer will extend inventory at destination
    """

    lot_number: str
    source_site: str
    destination_site: str
    quantity: int
    days_extended: int


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


def create_shipment(  # noqa: PLR0913
    session: Session,
    lot_number: str,
    site_name: str,
    shipment_date: date,
    quantity_shipped: int,
    anticipated_arrival_date: date | None = None,
) -> Shipment:
    """
    Create a new shipment in the database.

    Args:
        session: Database session
        lot_number: Reference to the lot being shipped
        site_name: Reference to the destination site
        shipment_date: Date when the shipment was sent
        quantity_shipped: Quantity of items in the shipment
        anticipated_arrival_date: Expected date of arrival (optional)

    Returns:
        The created shipment object

    Raises:
        IntegrityError: If the lot_number or site_name doesn't exist in the database
    """
    shipment = Shipment(
        lot_number=lot_number,
        site_name=site_name,
        shipment_date=shipment_date,
        quantity_shipped=quantity_shipped,
        anticipated_arrival_date=anticipated_arrival_date,
    )
    session.add(shipment)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    return shipment


def read_shipment(session: Session, shipment_id: int) -> Shipment | None:
    """
    Read a shipment from the database by its shipment ID.

    Args:
        session: Database session
        shipment_id: Unique identifier for the shipment

    Returns:
        The shipment object if found, None otherwise
    """
    return session.query(Shipment).filter_by(shipment_id=shipment_id).first()


def read_shipments(
    session: Session,
    lot_number: str | None = None,
    site_name: str | None = None,
) -> list[Shipment]:
    """
    Read shipments from the database with optional filtering.

    Args:
        session: Database session
        lot_number: Filter shipments by lot number
        site_name: Filter shipments by site name

    Returns:
        A list of shipment objects matching the criteria
    """
    query = session.query(Shipment)

    # Apply filters if provided
    if lot_number is not None:
        query = query.filter(Shipment.lot_number == lot_number)

    if site_name is not None:
        query = query.filter(Shipment.site_name == site_name)

    return query.all()


def update_shipment(  # noqa: PLR0913
    session: Session,
    shipment_id: int,
    lot_number: str | None = None,
    site_name: str | None = None,
    shipment_date: date | None = None,
    quantity_shipped: int | None = None,
    anticipated_arrival_date: date | None = None,
) -> Shipment | None:
    """
    Update a shipment in the database.

    Args:
        session: Database session
        shipment_id: Unique identifier for the shipment
        lot_number: New lot number (if None, not updated)
        site_name: New site name (if None, not updated)
        shipment_date: New shipment date (if None, not updated)
        quantity_shipped: New quantity shipped (if None, not updated)
        anticipated_arrival_date: New anticipated arrival date (if None, not updated)

    Returns:
        The updated shipment object if found, None otherwise

    Raises:
        IntegrityError: If the update violates database constraints
    """
    shipment = read_shipment(session, shipment_id)
    if shipment is None:
        return None

    if lot_number is not None:
        shipment.lot_number = lot_number
    if site_name is not None:
        shipment.site_name = site_name
    if shipment_date is not None:
        shipment.shipment_date = shipment_date
    if quantity_shipped is not None:
        shipment.quantity_shipped = quantity_shipped
    if anticipated_arrival_date is not None:
        shipment.anticipated_arrival_date = anticipated_arrival_date

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise

    return shipment


def delete_shipment(session: Session, shipment_id: int) -> bool:
    """
    Delete a shipment from the database.

    Args:
        session: Database session
        shipment_id: Unique identifier for the shipment to delete

    Returns:
        True if the shipment was deleted, False if not found

    Raises:
        IntegrityError: If the deletion would violate database constraints
    """
    shipment = read_shipment(session, shipment_id)
    if shipment is None:
        return False

    try:
        session.delete(shipment)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise

    return True


def create_inventory(
    session: Session, lot_number: str, site_name: str, current_quantity: int
) -> Inventory:
    """
    Create a new inventory record in the database.

    Args:
        session: Database session
        lot_number: Reference to the lot
        site_name: Reference to the site where the inventory is located
        current_quantity: Current quantity of items in stock

    Returns:
        The created inventory object

    Raises:
        IntegrityError: If a record with the same lot_number and site_name already exists
                        or if the lot_number or site_name doesn't exist in the database
    """
    inventory = Inventory(
        lot_number=lot_number,
        site_name=site_name,
        current_quantity=current_quantity,
        last_updated_date=date.today(),
    )
    session.add(inventory)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    return inventory


def read_inventory(
    session: Session,
    inventory_id: int | None = None,
    lot_number: str | None = None,
    site_name: str | None = None,
) -> Inventory | None:
    """
    Read an inventory record from the database.

    Args:
        session: Database session
        inventory_id: Unique identifier for the inventory record
        lot_number: Filter by lot number
        site_name: Filter by site name

    Returns:
        The inventory object if found, None otherwise

    Note:
        Either inventory_id or both lot_number and site_name must be provided.
    """
    if inventory_id is not None:
        return session.query(Inventory).filter_by(inventory_id=inventory_id).first()
    elif lot_number is not None and site_name is not None:
        return (
            session.query(Inventory)
            .filter_by(lot_number=lot_number, site_name=site_name)
            .first()
        )
    return None


def read_inventories(
    session: Session, lot_number: str | None = None, site_name: str | None = None
) -> list[Inventory]:
    """
    Read inventory records from the database with optional filtering.

    Args:
        session: Database session
        lot_number: Filter inventories by lot number
        site_name: Filter inventories by site name

    Returns:
        A list of inventory objects matching the criteria
    """
    query = session.query(Inventory)

    # Apply filters if provided
    if lot_number is not None:
        query = query.filter(Inventory.lot_number == lot_number)

    if site_name is not None:
        query = query.filter(Inventory.site_name == site_name)

    return query.all()


def update_inventory_quantity(
    session: Session, inventory_id: int, quantity_change: int
) -> Inventory | None:
    """
    Update the quantity of an inventory record by adding the quantity change.

    Args:
        session: Database session
        inventory_id: Unique identifier for the inventory record
        quantity_change: Change in quantity (positive for increase, negative for decrease)

    Returns:
        The updated inventory object if found, None otherwise

    Raises:
        ValueError: If the update would result in a negative quantity
        IntegrityError: If the update violates database constraints
    """
    inventory = read_inventory(session, inventory_id=inventory_id)
    if inventory is None:
        return None

    new_quantity = inventory.current_quantity + quantity_change
    if new_quantity < 0:
        raise ValueError("Inventory quantity cannot be negative")

    inventory.current_quantity = new_quantity
    inventory.last_updated_date = date.today()

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise

    return inventory


def record_stock_arrival(session: Session, shipment_id: int) -> Inventory | None:
    """
    Update inventory when a shipment arrives at its destination.

    Args:
        session: Database session
        shipment_id: The ID of the shipment that has arrived

    Returns:
        The updated inventory record if the shipment exists, None otherwise

    Raises:
        ValueError: If trying to record arrival for a shipment with no quantity
        IntegrityError: If there are database constraint violations

    Note:
        This function will create a new inventory record if one doesn't exist
        for the lot and site combination.
    """
    shipment = read_shipment(session, shipment_id)
    if shipment is None:
        return None

    if shipment.quantity_shipped <= 0:
        raise ValueError("Cannot record arrival for a shipment with no quantity")

    # Check if inventory record exists for this lot and site
    inventory = read_inventory(
        session, lot_number=shipment.lot_number, site_name=shipment.site_name
    )

    try:
        if inventory is None:
            # Create a new inventory record
            inventory = create_inventory(
                session,
                lot_number=shipment.lot_number,
                site_name=shipment.site_name,
                current_quantity=shipment.quantity_shipped,
            )
        else:
            # Update existing inventory
            inventory.current_quantity += shipment.quantity_shipped
            inventory.last_updated_date = date.today()
            session.commit()
    except IntegrityError:
        session.rollback()
        raise

    return inventory


def record_stock_usage(
    session: Session, lot_number: str, site_name: str, quantity_used: int
) -> Inventory | None:
    """
    Update inventory when stock is used at a site.

    Args:
        session: Database session
        lot_number: The lot number of the used stock
        site_name: The site where the stock was used
        quantity_used: The amount of stock used (must be positive)

    Returns:
        The updated inventory record if it exists, None otherwise

    Raises:
        ValueError: If quantity_used is not positive or would result in negative inventory
        IntegrityError: If there are database constraint violations
    """
    if quantity_used <= 0:
        raise ValueError("Quantity used must be positive")

    inventory = read_inventory(session, lot_number=lot_number, site_name=site_name)
    if inventory is None:
        return None

    if inventory.current_quantity < quantity_used:
        raise ValueError("Cannot use more stock than is available in inventory")

    inventory.current_quantity -= quantity_used
    inventory.last_updated_date = date.today()

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise

    return inventory


def calculate_usage_rate(
    session: Session, lot_number: str, site_name: str
) -> tuple[float, int, date] | None:
    """
    Calculate the rate at which a site is consuming a particular lot.

    Args:
        session: Database session
        lot_number: The lot number to check
        site_name: The site name to check

    Returns:
        A tuple containing:
            - The usage rate in units per day (float)
            - The total quantity used (int)
            - The date of the first inventory record (date)
        Returns None if there is insufficient data to calculate a rate

    Note:
        The usage rate is calculated based on the change in inventory
        from the earliest recorded inventory to the current level.
        If there is no usage history or only one inventory record,
        it will return None as there is not enough data to calculate a rate.
    """
    # Check if inventory exists for this lot and site
    inventory = read_inventory(session, lot_number=lot_number, site_name=site_name)
    if inventory is None:
        return None

    # Get the shipments ordered by date to identify initial quantity
    shipments = (
        session.query(Shipment)
        .filter_by(lot_number=lot_number, site_name=site_name)
        .order_by(Shipment.shipment_date)
        .all()
    )

    if not shipments:
        # No shipments, so we can't calculate a usage rate
        return None

    # Get the first shipment and its date
    first_shipment = shipments[0]
    first_date = first_shipment.shipment_date

    # Calculate total shipped quantity (from all shipments)
    total_shipped = sum(shipment.quantity_shipped for shipment in shipments)

    # Current inventory level
    current_quantity = inventory.current_quantity

    # Calculate total used
    total_used = total_shipped - current_quantity

    # If no usage, return zero rate
    if total_used <= 0:
        return 0.0, 0, first_date

    # Calculate days elapsed since first shipment
    days_elapsed = (date.today() - first_date).days

    # Avoid division by zero
    if days_elapsed <= 0:
        return None

    # Calculate usage rate (units per day)
    usage_rate = total_used / days_elapsed

    return usage_rate, total_used, first_date


def predict_runout_date(
    session: Session, lot_number: str, site_name: str
) -> date | None:
    """
    Predict the date when a lot will run out at a specific site based on usage rate.

    Args:
        session: Database session
        lot_number: The lot number to check
        site_name: The site name to check

    Returns:
        The predicted run-out date or None if it can't be calculated
        (e.g., if there's no inventory, no usage history, or zero usage rate)

    Note:
        This function uses the current inventory level and historical usage rate
        to predict when the inventory will be depleted. If the usage rate is
        zero or can't be calculated, it returns None.
    """
    # Check if inventory exists for this lot and site
    inventory = read_inventory(session, lot_number=lot_number, site_name=site_name)
    if inventory is None:
        return None

    # Get current inventory level
    current_quantity = inventory.current_quantity

    # If no inventory, it's already run out
    if current_quantity <= 0:
        return date.today()

    # Calculate usage rate
    rate_info = calculate_usage_rate(
        session, lot_number=lot_number, site_name=site_name
    )
    if rate_info is None:
        # Can't calculate usage rate
        return None

    usage_rate, _, _ = rate_info

    # If no usage, inventory won't run out
    if usage_rate <= 0:
        return None

    # Calculate days until run-out
    days_until_runout = int(current_quantity / usage_rate)

    # Calculate run-out date
    runout_date = date.today() + timedelta(days=days_until_runout)

    return runout_date


def predict_leftover_quantity(
    session: Session, lot_number: str, site_name: str
) -> int | None:
    """
    Predict how much of a lot will be leftover or short by its expiration date.

    Args:
        session: Database session
        lot_number: The lot number to check
        site_name: The site name to check

    Returns:
        The predicted leftover quantity (positive means leftover, negative means shortage)
        or None if it can't be calculated (e.g., if there's no inventory, no usage history,
        or zero usage rate)

    Note:
        This function uses the current inventory level, historical usage rate,
        and lot expiration date to predict the leftover quantity. A positive value
        indicates inventory will remain at expiration, while a negative value
        indicates a shortage before expiration (run out before expiry).
    """
    # Check if inventory exists and get current quantity
    inventory = read_inventory(session, lot_number=lot_number, site_name=site_name)
    if inventory is None:
        return None

    current_quantity = inventory.current_quantity

    # If no inventory, nothing will be leftover
    if current_quantity <= 0:
        return 0

    # Get the lot to check its expiration date
    lot = read_lot(session, lot_number=lot_number)
    if lot is None:
        return None

    # Get expiration date
    expiration_date = lot.expiration_date

    # If already expired, return current quantity (it's all leftover)
    if expiration_date <= date.today():
        return current_quantity

    # Calculate usage rate
    rate_info = calculate_usage_rate(
        session, lot_number=lot_number, site_name=site_name
    )

    # Handle cases where usage rate can't be calculated or is zero
    if rate_info is None or rate_info[0] <= 0:
        return current_quantity

    usage_rate = rate_info[0]

    # Calculate days until expiration and expected usage
    days_until_expiration = (expiration_date - date.today()).days
    expected_usage = int(days_until_expiration * usage_rate)

    # Calculate leftover quantity (can be negative if expected to run short)
    return current_quantity - expected_usage


# Constants for inventory transfers
LOW_INVENTORY_DAYS = 30  # Days until run-out to consider "low"
MIN_EXTENSION_DAYS = 14  # Minimum days to extend inventory with a transfer
SURPLUS_THRESHOLD = 0.05  # Min percentage of initial quantity to consider "surplus"


def _get_sites_with_low_inventory(
    session: Session, lot_number: str, sites_with_lot: list[Inventory]
) -> list[dict]:
    """
    Identify sites with low inventory of a specific lot.

    Args:
        session: Database session
        lot_number: Lot number to check
        sites_with_lot: List of inventory records for the lot across different sites

    Returns:
        List of dictionaries containing information about sites with low inventory
    """
    low_sites = []

    for inv in sites_with_lot:
        if inv.current_quantity <= 0:
            continue  # Skip sites with no inventory

        runout_date = predict_runout_date(session, inv.lot_number, inv.site_name)
        if runout_date is not None:
            days_until_runout = (runout_date - date.today()).days
            if 0 < days_until_runout <= LOW_INVENTORY_DAYS:
                # Calculate usage rate for this site
                rate_info = calculate_usage_rate(session, inv.lot_number, inv.site_name)
                if rate_info is not None and rate_info[0] > 0:
                    low_sites.append(
                        {
                            "site_name": inv.site_name,
                            "inventory": inv,
                            "days_until_runout": days_until_runout,
                            "usage_rate": rate_info[0],
                        }
                    )

    return low_sites


def _get_sites_with_surplus_inventory(
    session: Session, lot_number: str, sites_with_lot: list[Inventory]
) -> list[dict]:
    """
    Identify sites with surplus inventory of a specific lot.

    Args:
        session: Database session
        lot_number: Lot number to check
        sites_with_lot: List of inventory records for the lot across different sites

    Returns:
        List of dictionaries containing information about sites with surplus inventory
    """
    surplus_sites = []
    lot = read_lot(session, lot_number)
    if lot is None:
        return []

    for inv in sites_with_lot:
        leftover = predict_leftover_quantity(session, inv.lot_number, inv.site_name)
        # Site has surplus if it has positive leftover quantity exceeding the threshold
        if leftover is not None and leftover > 0:
            percent_leftover = leftover / lot.initial_quantity
            if percent_leftover >= SURPLUS_THRESHOLD:
                # Calculate usage rate for this site
                rate_info = calculate_usage_rate(session, inv.lot_number, inv.site_name)
                usage_rate = (
                    0 if rate_info is None or rate_info[0] <= 0 else rate_info[0]
                )

                # Calculate how much can be safely transferred
                # (leave at least 30 days of inventory at the source)
                safe_transfer = leftover
                if usage_rate > 0:
                    min_needed = int(LOW_INVENTORY_DAYS * usage_rate)
                    if inv.current_quantity - min_needed < safe_transfer:
                        safe_transfer = max(0, inv.current_quantity - min_needed)

                if safe_transfer > 0:
                    surplus_sites.append(
                        {
                            "site_name": inv.site_name,
                            "inventory": inv,
                            "leftover": leftover,
                            "safe_transfer": safe_transfer,
                        }
                    )

    return surplus_sites


def _create_transfer_suggestions(
    lot_number: str, low_sites: list[dict], surplus_sites: list[dict]
) -> list[TransferSuggestion]:
    """
    Create transfer suggestions between sites with low and surplus inventory.

    Args:
        lot_number: Lot number for the transfers
        low_sites: Sites with low inventory
        surplus_sites: Sites with surplus inventory

    Returns:
        List of transfer suggestions
    """
    suggestions = []
    # Make a copy of surplus_sites to avoid modifying the original
    surplus_sites_copy = surplus_sites.copy()

    # For each low site, find the best surplus site to transfer from
    for low_site in low_sites:
        if not surplus_sites_copy:
            continue

        # Sort surplus sites by safe_transfer amount (descending)
        surplus_sites_copy.sort(key=lambda x: int(x["safe_transfer"]), reverse=True)

        # Choose the site with the most available inventory to transfer
        source_site = surplus_sites_copy[0]

        # Calculate how much to transfer
        # (enough to extend inventory by at least MIN_EXTENSION_DAYS)
        needed_quantity = int(MIN_EXTENSION_DAYS * float(low_site["usage_rate"]))
        transfer_quantity = min(needed_quantity, int(source_site["safe_transfer"]))

        if transfer_quantity > 0:
            # Calculate how many days this transfer will extend the inventory
            days_extended = int(transfer_quantity / float(low_site["usage_rate"]))

            # Create a transfer suggestion
            suggestion = TransferSuggestion(
                lot_number=lot_number,
                source_site=str(source_site["site_name"]),
                destination_site=str(low_site["site_name"]),
                quantity=transfer_quantity,
                days_extended=days_extended,
            )

            suggestions.append(suggestion)

            # Update the source site's safe_transfer amount for subsequent suggestions
            source_site["safe_transfer"] -= transfer_quantity

    return suggestions


def suggest_inventory_transfers(session: Session) -> list[TransferSuggestion]:
    """
    Identify sites with surplus inventory of lots that are running low at other sites
    and suggest transfers.

    Args:
        session: Database session

    Returns:
        A list of transfer suggestions, each containing source site, destination site,
        lot number, transfer quantity, and days extended.

    Note:
        This function finds lots that will run out in less than 30 days at one site
        but have surplus inventory at another site. It suggests transferring enough
        inventory to extend the runout date by at least 14 days, if possible.
    """
    suggestions = []

    # Get all inventory items
    inventories = read_inventories(session)

    # Group inventories by lot number
    lot_sites: dict[str, list[Inventory]] = {}
    for inv in inventories:
        if inv.lot_number not in lot_sites:
            lot_sites[inv.lot_number] = []
        lot_sites[inv.lot_number].append(inv)

    # For each lot that exists in multiple sites
    for lot_number, sites_with_lot in lot_sites.items():
        if len(sites_with_lot) <= 1:
            continue  # Skip lots that are only at one site

        # Find sites where this lot is running low
        low_sites = _get_sites_with_low_inventory(session, lot_number, sites_with_lot)
        if not low_sites:
            continue  # No sites running low on this lot

        # Find sites with surplus inventory of this lot
        surplus_sites = _get_sites_with_surplus_inventory(
            session, lot_number, sites_with_lot
        )
        if not surplus_sites:
            continue  # No sites with surplus for this lot

        # Create transfer suggestions between low and surplus sites
        lot_suggestions = _create_transfer_suggestions(
            lot_number, low_sites, surplus_sites
        )
        suggestions.extend(lot_suggestions)

    return suggestions
