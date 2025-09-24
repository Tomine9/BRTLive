from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Bus(Base):
    __tablename__ = "buses"
    
    id = Column(Integer, primary_key=True, index=True)
    bus_number = Column(String(20), unique=True, index=True, nullable=False)
    license_plate = Column(String(15), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    model = Column(String(50))
    year = Column(Integer)
    is_active = Column(Boolean, default=True)
    current_route_id = Column(Integer, ForeignKey("routes.id"))
    current_driver_id = Column(Integer, ForeignKey("drivers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    current_route = relationship("Route", back_populates="buses")
    current_driver = relationship("Driver", back_populates="current_bus")
    tracking_records = relationship("BusTracking", back_populates="bus")