from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from enum import Enum
from Bus import BusStatus
from .Base import Base

class Tracking (Base):
    __table__name = "trackings"
    id = Column(Integer, primary_key= True , index = True)
    bus_id = Column(Integer , ForeignKey("buses.id"))
    route_id = Column(Integer, ForeignKey("routes.id"))
    longitude = Column(Float , nullable= False)
    Latitude = Column(Float , nullable= False)
    speed_km = Column( Float, default= 0.0)
    heading = Column( Float, nullable= False)
    last_updated = Column(DateTime, default= datetime.now(timezone.utc), onupdate= datetime.now(timezone.utc))

    bus = relationship("Bus", back_populates= "tracking")
    driver = relationship("Driver", back_populates="tracking")

