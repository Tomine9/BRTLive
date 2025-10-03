from datetime import datetime, timezone
from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Enum

class BusStatus(Enum):
    IN_TRANSIT = "in_transit"
    AT_TERMINAL = "at_terminal"
    OUT_OF_SERVICE = "out_of_service"
    MAINTENANCE = "maintenance"

class Bus(Base):
    __tablename__ = "buses"
    id = Column(Integer, primary_key= True , index= True)
    plate_number = Column(String(25),unique= True , nullable= False)
    capacity = Column(Integer, default= 50)
    current_passenger_count = Column( Integer, default=0)
    route_id = Column(Integer, ForeignKey("routes.id"))
    status = Column(BusStatus, default = BusStatus.OUT_OF_SERVICE)
    is_active = Column(Boolean, default= True)
    created_at = Column(DateTime, default= datetime.now(timezone.utc))
    current_route_id = Column(Integer, ForeignKey("routes.id"), nullable= True)

    route = relationship("Route", back_populates="buses")
    tracking = relationship("tracking", uselist= False , back_populates= "bus")
    bus_assignments = relationship("BusAssignment", back_populates= "bus")
    location_history = relationship ("LocationHistory", back_populates= "bus", order_by= "LocationHistory.timestamp.desc()")
