from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Terminal(Base):
    """Major terminal/station model with extended features"""
    __tablename__ = "terminals"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    terminal_code = Column(String(20), unique=True, index=True, nullable=False)  # e.g., "TERM_CENTRAL"
    bus_stop_id = Column(Integer, ForeignKey("bus_stops.id"), nullable=False, unique=True)
    
    # Terminal-specific information
    terminal_type = Column(String(50), default="standard")  # standard, interchange, depot
    max_bus_capacity = Column(Integer, default=10)  # Maximum buses that can be at terminal
    number_of_platforms = Column(Integer, default=1)
    has_ticket_office = Column(Boolean, default=False)
    has_waiting_area = Column(Boolean, default=True)
    has_restrooms = Column(Boolean, default=False)
    has_food_services = Column(Boolean, default=False)
    has_wifi = Column(Boolean, default=False)
    has_security = Column(Boolean, default=False)
    
    # Operational characteristics
    is_interchange = Column(Boolean, default=False)  # Connects multiple routes
    is_depot = Column(Boolean, default=False)  # Bus storage and maintenance
    layover_time_minutes = Column(Integer, default=5)  # Standard layover time
    rush_hour_layover_minutes = Column(Integer, default=3)  # Reduced layover during rush
    
    # Passenger services
    passenger_information_display = Column(Boolean, default=True)  # Digital displays
    audio_announcements = Column(Boolean, default=True)
    cctv_coverage = Column(Boolean, default=False)
    emergency_phone = Column(Boolean, default=False)
    
    # Contact and management
    manager_name = Column(String(100))
    manager_phone = Column(String(20))
    control_room_phone = Column(String(20))
    emergency_contact = Column(String(20))
    
    # Revenue and statistics
    daily_passenger_count = Column(Integer, default=0)
    monthly_passenger_count = Column(Integer, default=0)
    revenue_per_day = Column(Float, default=0.0)
    
    # Status and operations
    current_status = Column(String(50), default="operational")  # operational, maintenance, closed
    last_inspection = Column(DateTime(timezone=True))
    next_maintenance = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional data
    facilities_json = Column(JSON)  # Flexible facilities data
    operational_notes = Column(Text)
    
    # Relationships
    bus_stop = relationship("BusStop", back_populates="terminal_details")
    buses = relationship("Bus", secondary="bus_terminal_assignments", back_populates="terminals") # Many-to-many with buses
    
    def __repr__(self):
        return f"<Terminal(code='{self.terminal_code}', type='{self.terminal_type}', status='{self.current_status}')>"