from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from .Base import Base


class RouteStop(Base):
    __tablename__ = "route_stops"
    id = Column(Integer, index= True,primary_key= True)
    route_id = Column(Integer, ForeignKey("route.id"))
    terminal_id = Column(Integer, ForeignKey("terminal.id"))
    stop_order = Column(Integer, nullable= False)
    estimated_travel_time_minutes =Column(Integer, default=5)

    route = relationship("Route", back_populates= "route_stops")
    terminal = relationship("Terminal")