from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from .Base import Base

class Driver(Base):
    __table__name = "drivers"
    id = Column(Integer, primary_key= True, index= True)
    employees_id = Column(String(20), unique=True , nullable=False)
    first_name = Column(String(50), nullable= False)
    last_name = Column (String(50), nullable= False)
    license_id = Column(String(50), unique= True, nullable= False)
    phone_number = Column(String(15), unique= True , nullable= False)
    is_active = Column(Boolean,default= True)
    created_at = Column(DateTime, default = datetime.now(timezone.utc))

    bus_assignment = relationship("BusAssignment", back_populates= "driver")
    tracking = relationship("Tracking", back_populates="driver")
