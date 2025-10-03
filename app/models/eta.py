from sqlalchemy import Column, Boolean, String, Integer,Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .Base import Base
from datetime import datetime, timezone

class Eta(Base):
    __tablename__ = "eta"
    id = Column(Integer, primary_key= True , index= True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)   
    terminal_id = Column(Integer, ForeignKey("terminals.id"), nullable=False)
    estimated_arrival_time = Column(DateTime, nullable=False)
    estimated_minutes_away = Column(Integer, nullable=False)
    confidence_level = Column(Float, default=0.8)
    prediction_method = Column(String(50), default="real_time")
    calculated_from_phone_location = Column(Boolean, default=True)
    last_phone_update_used = Column(DateTime, nullable=True)
    calculated_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=datetime.now(timezone.utc),onupdate=datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    bus = relationship("Bus", back_populates="eta")
    terminal = relationship("Terminal", back_populates="eta")
    user = relationship("User", back_populates="eta")
    


