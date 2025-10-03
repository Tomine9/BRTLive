from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from .Base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, unique=True)
    is_active= Column(Boolean, default=True) 
    last_enter = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    
    routes= relationship("Route", back_populates="user")
    terminals= relationship("Terminal", back_populates="user")
    eta = relationship("Eta", back_populates="user")
    tracking = relationship("Tracking", back_populates="user")

    

