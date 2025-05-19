# Define SQLAlchemy models here
# Example:
# from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
# from sqlalchemy.orm import sessionmaker, relationship
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

# class Lot(Base):
#     __tablename__ = 'lots'
#     lot_number = Column(String, primary_key=True)
#     expiration_date = Column(Date)
#     initial_quantity = Column(Integer)
#     shipments = relationship("Shipment", back_populates="lot")
#     inventory = relationship("Inventory", back_populates="lot")

# class Site(Base):
#     __tablename__ = 'sites'
#     site_name = Column(String, primary_key=True)
#     contact_info = Column(String)
#     shipments = relationship("Shipment", back_populates="site")
#     inventory = relationship("Inventory", back_populates="site")

# class Shipment(Base):
#     __tablename__ = 'shipments'
#     shipment_id = Column(Integer, primary_key=True, autoincrement=True)
#     lot_number = Column(String, ForeignKey('lots.lot_number'))
#     site_name = Column(String, ForeignKey('sites.site_name'))
#     shipment_date = Column(Date)
#     quantity_shipped = Column(Integer)
#     anticipated_arrival_date = Column(Date)
#     lot = relationship("Lot", back_populates="shipments")
#     site = relationship("Site", back_populates="shipments")

# class Inventory(Base):
#     __tablename__ = 'inventory'
#     inventory_id = Column(Integer, primary_key=True, autoincrement=True)
#     lot_number = Column(String, ForeignKey('lots.lot_number'))
#     site_name = Column(String, ForeignKey('sites.site_name'))
#     current_quantity = Column(Integer)
#     last_updated_date = Column(Date)
#     lot = relationship("Lot", back_populates="inventory")
#     site = relationship("Site", back_populates="inventory")

# # engine = create_engine('sqlite:///inventory.db') # Or path to network drive
# # Base.metadata.create_all(engine)
# # Session = sessionmaker(bind=engine)
# # session = Session()
