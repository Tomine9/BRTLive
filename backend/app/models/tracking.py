from app.database import Base
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class BusTracking (Base):
    __tablename__ = "trackings"
    id = Column(Integer, primary_key= True , index = True)
    bus_id = Column(Integer , ForeignKey("buses.id"))
    route_id = Column(Integer, ForeignKey("routes.id"))
    longitude = Column(Float , nullable= False)
    Latitude = Column(Float , nullable= False)
    speed_km = Column(Float, default= 0.0)
    heading = Column(Float, nullable= False)
    last_updated = Column(DateTime, default= datetime.now(timezone.utc), onupdate= datetime.now(timezone.utc))
    gps_timestamp = Column(DateTime, default= datetime.now(timezone.utc))
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable= True)

    bus = relationship("Bus", back_populates= "tracking")
    driver = relationship("Driver", back_populates="tracking")

