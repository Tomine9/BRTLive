from app.database import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key= True, index= True)
    employees_id = Column(String(20), unique=True , nullable=False)
    first_name = Column(String(50), nullable= False)
    last_name = Column (String(50), nullable= False)
    license_id = Column(String(50), unique= True, nullable= False)
    phone_number = Column(String(15), unique= True , nullable= False)
    is_active = Column(Boolean,default= True)
    created_at = Column(DateTime, default = datetime.now(timezone.utc))
    is_on_duty = Column(Boolean, default= False)
    is_available: Mapped[bool] = mapped_column(Boolean, default= True)
    
    # Relationships
    bus_assignment = relationship("BusAssignment", back_populates= "driver")
    tracking = relationship("Tracking", back_populates="driver")
