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
    current_shift_id = Column(Integer, ForeignKey("bus_assignment.id"), nullable=True)

    is_active = Column(Boolean,default= True)
    is_verified = Column(Boolean, default=False)
    is_on_shift = Column(Boolean, default=False)
    created_at = Column(DateTime, default = datetime.now(timezone.utc))

    password_hash = Column(String(255), nullable=False)

    bus_assignment = relationship("BusAssignment", back_populates= "driver") 
    admins = relationship("Admin", back_populates="drivers")
    
