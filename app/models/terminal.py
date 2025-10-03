

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from .Base import Base

class Terminal(Base):
    __tablename__ = "terminals"
    id = Column(Integer, primary_key=True, index= True)
    name = Column(String(100), unique= True, nullable= False)
    location = Column(String(225), nullable= False) 
    longitude = Column(Float, nullable= False)
    latitude = Column( Float, nullable= False)
    created_at = Column(DateTime, default = datetime.now(timezone.utc))

    routes_starting = relationship("Route", foreign_keys = "Route.start_terminal_id", back_populates="start_terminal")
    routes_ending = relationship("Route",foreign_keys= "Route.end_terminal_id", back_populates="end_terminal")
    eta = relationship("Eta", back_populates="terminal")
