from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from enum import Enum
from app.database import Base

# =============================================================================
# 1. ROUTE MODEL - Main route definition (e.g., Red Line, Blue Line)
# =============================================================================

class Route(Base):
    """Main route model representing a BRT service line"""
    __tablename__ = "routes"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    route_code = Column(String(20), unique=True, index=True, nullable=False)  # e.g., "RED_LINE", "BL_001"
    route_name = Column(String(100), nullable=False, index=True)  # e.g., "Red Line", "Blue Line Express"
    
    # Route characteristics
    route_type = Column(String(50), default="standard")  # standard, express, limited, shuttle
    color_code = Column(String(10))  # Hex color for maps/displays (#FF0000 for red line)
    description = Column(Text)  # Detailed route description
    
    # Operational data
    total_distance_km = Column(Float)  # Total route distance (one direction)
    estimated_journey_time_minutes = Column(Integer)  # End-to-end journey time
    service_frequency_peak_minutes = Column(Integer, default=10)  # Peak hour frequency
    service_frequency_offpeak_minutes = Column(Integer, default=15)  # Off-peak frequency
    
    # Service times
    first_service_time = Column(String(8), default="05:00")  # "HH:MM:SS" format
    last_service_time = Column(String(8), default="23:00")
    operates_weekends = Column(Boolean, default=True)
    operates_holidays = Column(Boolean, default=False)
    
    # Status and management
    is_active = Column(Boolean, default=True, index=True)
    is_operational = Column(Boolean, default=True)  # Can be temporarily suspended
    maintenance_mode = Column(Boolean, default=False)
    
    # Administrative
    managed_by = Column(String(100))  # Operating company
    route_manager_name = Column(String(100))
    route_manager_phone = Column(String(20))
    emergency_contact = Column(String(20))
    
    # Performance metrics
    daily_ridership = Column(Integer, default=0)
    monthly_ridership = Column(Integer, default=0)
    on_time_performance = Column(Float, default=0.0)  # 0-100 percentage
    customer_satisfaction = Column(Float, default=0.0)  # 0-5 rating
    
    # Financial
    fare_amount = Column(Float, default=0.0)  # Standard fare for this route
    daily_revenue = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=text('NOW()'))
    updated_at = Column(DateTime(timezone=True), onupdate=text('NOW()'))
    last_schedule_update = Column(DateTime(timezone=True))
    
    # Metadata
    route_metadata = Column(JSON)  # Flexible additional data
    special_notes = Column(Text)  # Operational notes
    
    # Relationships
    route_directions = relationship("RouteDirection", back_populates="route", cascade="all, delete-orphan")
    buses = relationship("Bus", back_populates="current_route")
    
    # Database indexes
    __table_args__ = (
        Index('ix_routes_active_operational', 'is_active', 'is_operational'),
        Index('ix_routes_type', 'route_type'),
    )
    
    @hybrid_property
    def is_currently_operational(self) -> bool:
        """Check if route is operational right now"""
        if not (self.is_active and self.is_operational and not self.maintenance_mode):
            return False
        
        current_time = datetime.now().time()
        current_day = datetime.now().weekday()  # 0 = Monday, 6 = Sunday
        
        try:
            first_time = datetime.strptime(self.first_service_time, "%H:%M").time()
            last_time = datetime.strptime(self.last_service_time, "%H:%M").time()
            
            # Check weekend operations
            if current_day >= 5 and not self.operates_weekends:  # Weekend
                return False
            
            # Check time range
            if first_time <= last_time:
                return first_time <= current_time <= last_time
            else:  # Overnight service
                return current_time >= first_time or current_time <= last_time
        except ValueError:
            return True  # Default to operational if parsing fails
    
    @hybrid_property
    def total_stops_count(self) -> int:
        """Get total number of unique stops across all directions"""
        if not self.route_directions:
            return 0
        
        all_stop_ids = set()
        for direction in self.route_directions:
            for route_stop in direction.route_stops:
                all_stop_ids.add(route_stop.stop_id)
        
        return len(all_stop_ids)
    
    def __repr__(self):
        return f"<Route(code='{self.route_code}', name='{self.route_name}', type='{self.route_type}')>"