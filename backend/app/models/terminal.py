from app.database import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

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
