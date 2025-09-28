from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from .Base import Base

class Route(Base):
    __table__name = "routes"
    id = Column(Integer,primary_key=True , index= True)
    name = Column(String(50), unique= True, nullable = False)
    start_terminal_id = Column(Integer, ForeignKey("routes.id"))
    end_terminal_id = Column( Integer,ForeignKey("routes.id"))
    distance_km = Column(Float, default= 0.0)
    estimated_duration_minutes = Column(Integer, default= 45)
    created_at = Column(DateTime, default = datetime.now(timezone.utc))

    start_terminal = relationship("Terminal", foreign_keys=[start_terminal_id], back_populates= "routes_starting")
    end_terminal = relationship("Terminal", foreign_keys=[end_terminal_id], back_populates="routes_ending")
    buses = relationship("Bus", back_populates="route")
    route_stops = relationship("Route_stop", back_populates= "route", order_by= "RouteStop.stop_order")
