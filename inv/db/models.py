# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
from datetime import date
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Lot(Base):
    """
    Represents a batch of products with a unique lot number.
    
    Attributes:
        lot_number: Unique identifier for the lot
        expiration_date: Date when the lot will expire
        initial_quantity: The original quantity of items in the lot
        shipments: List of shipments related to this lot
        inventory: List of inventory records for this lot
    """
    __tablename__ = 'lots'
    
    lot_number: Mapped[str] = mapped_column(String, primary_key=True)
    expiration_date: Mapped[date] = mapped_column(Date)
    initial_quantity: Mapped[int] = mapped_column(Integer)
    
    shipments: Mapped[List["Shipment"]] = relationship("Shipment", back_populates="lot")
    inventory: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="lot")


class Site(Base):
    """
    Represents a physical location where inventory is stored.
    
    Attributes:
        site_name: Unique identifier for the site
        contact_info: Contact information for the site
        shipments: List of shipments to/from this site
        inventory: List of inventory records at this site
    """
    __tablename__ = 'sites'
    
    site_name: Mapped[str] = mapped_column(String, primary_key=True)
    contact_info: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    shipments: Mapped[List["Shipment"]] = relationship("Shipment", back_populates="site")
    inventory: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="site")


class Shipment(Base):
    """
    Represents movement of lots between sites.
    
    Attributes:
        shipment_id: Unique identifier for the shipment
        lot_number: Reference to the lot being shipped
        site_name: Reference to the destination site
        shipment_date: Date when the shipment was sent
        quantity_shipped: Quantity of items in the shipment
        anticipated_arrival_date: Expected date of arrival
        lot: The lot being shipped
        site: The destination site
    """
    __tablename__ = 'shipments'
    
    shipment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_number: Mapped[str] = mapped_column(String, ForeignKey('lots.lot_number'))
    site_name: Mapped[str] = mapped_column(String, ForeignKey('sites.site_name'))
    shipment_date: Mapped[date] = mapped_column(Date)
    quantity_shipped: Mapped[int] = mapped_column(Integer)
    anticipated_arrival_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    lot: Mapped["Lot"] = relationship("Lot", back_populates="shipments")
    site: Mapped["Site"] = relationship("Site", back_populates="shipments")


class Inventory(Base):
    """
    Tracks the current state of lots at specific sites.
    
    Attributes:
        inventory_id: Unique identifier for the inventory record
        lot_number: Reference to the lot
        site_name: Reference to the site where the inventory is located
        current_quantity: Current quantity of items in stock
        last_updated_date: Date when the inventory was last updated
        lot: The lot being tracked
        site: The site where the inventory is located
    """
    __tablename__ = 'inventory'
    
    inventory_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_number: Mapped[str] = mapped_column(String, ForeignKey('lots.lot_number'))
    site_name: Mapped[str] = mapped_column(String, ForeignKey('sites.site_name'))
    current_quantity: Mapped[int] = mapped_column(Integer)
    last_updated_date: Mapped[date] = mapped_column(Date)
    
    lot: Mapped["Lot"] = relationship("Lot", back_populates="inventory")
    site: Mapped["Site"] = relationship("Site", back_populates="inventory")


def init_db(db_path: str = "sqlite:///inventory.db") -> sessionmaker:
    """
    Initialize the database and return a session maker.
    
    Args:
        db_path: Path to the database. Defaults to a local SQLite database.
                Can be configured to use a network drive.
    
    Returns:
        A sessionmaker that can be used to create database sessions.
    """
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session
