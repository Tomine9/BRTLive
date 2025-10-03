from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from .Base import Base

class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key= True, index= True)
    employees_id = Column(String(20), unique=True , nullable=False)
    first_name = Column(String(50), nullable= False)
    last_name = Column (String(50), nullable= False)
    license_id = Column(String(50), unique= True, nullable= False)
    phone_number = Column(String(15), unique= True , nullable= False, index=True)
    phone_device_info = Column(String(255), unique=True, nullable=True)
    last_location_update = Column(DateTime, nullable=True)
    is_tracking_enabled = Column(Boolean, default=False)
    is_active = Column(Boolean,default= True)
    created_at = Column(DateTime, default = datetime.now(timezone.utc))

    bus_assignment = relationship("BusAssignment", back_populates= "driver") 
    
