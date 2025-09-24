from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class BusTracking(Base):
    __tablename__ = "bus_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, default=0.0)
    heading = Column(Float)  # Direction in degrees
    altitude = Column(Float)
    accuracy = Column(Float)  # GPS accuracy in meters
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(20), default="mobile")  # mobile, gps_device, etc.
    
    # Relationships
    bus = relationship("Bus", back_populates="tracking_records")