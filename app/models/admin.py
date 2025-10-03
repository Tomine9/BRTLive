from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from enum import Enum
from .Base import Base

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    is_active= Column(Boolean, default=True)
    is_super_admin =Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)

    bus = relationship('Bus', back_populates="admins")
    drivers= relationship("Driver", back_populates="admins")
