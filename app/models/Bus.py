from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from enum import Enum
from .Base import Base

class BusStatus(Enum):
    IN_TRANSIT = "in_transit"
    AT_TERMINAL = "at_terminal"
    OUT_OF_SERVICE = "out_of_service"
    MAINTENANCE = "maintenance"

class Bus(Base):
    __tablename__ = "buses"
    id = Column(Integer, primary_key=True , index=True)
    plate_number = Column(String(25),unique=True , nullable=False)
    capacity = Column(Integer, default=50)
    current_passenger_count = Column( Integer, default=0)
    route_id = Column(Integer, ForeignKey("routes.id"))
    status = Column(Enum(BusStatus), default=BusStatus.OUT_OF_SERVICE)
    is_available = Column(Boolean, default=True)
    current_shift_id = Column(Integer, ForeignKey("bus_assignments.id"))
    current_driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    route = relationship("Route", back_populates="buses")
    tracking = relationship("tracking", uselist=False , back_populates="bus")
    bus_assignment= relationship("BusAssignment", back_populates="bus")
    current_driver = relationship("Driver", foreign_keys=[current_driver_id])
    eta = relationship("Eta", back_populates="bus")
    admins= relationship("Admin", back_populates="bus")
    

