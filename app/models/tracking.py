from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from enum import Enum
from Bus import BusStatus
from .Base import Base

class Tracking (Base):
    __tablename__ = "trackings"
    id = Column(Integer, primary_key= True , index = True)
    bus_id = Column(Integer , ForeignKey("buses.id"), unique=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    driver_phone_number = Column(String(20), nullable=True)
    longitude = Column(Float , nullable= False)
    Latitude = Column(Float , nullable= False)
    accuracy_meters = Column(Float, default=10.0)
    speed_km = Column( Float, default= 0.0)
    heading = Column( Float, nullable= True)
    altitude = Column(Float, nullable=True)
    phone_battery_level = Column(Integer, nullable=True)
    is_charging = Column(Boolean, default=False)
    network_type = Column(String(10),nullable=True)
    signal_strength = Column(String(10), nullable=True)
    last_phone_ping = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default= datetime.now(timezone.utc), onupdate= datetime.now(timezone.utc))

    bus = relationship("Bus", back_populates= "tracking")
    driver = relationship("Driver", back_populates="tracking")
    user = relationship("User", back_populates="tracking")

