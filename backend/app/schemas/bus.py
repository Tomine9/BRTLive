from pydantic import BaseModel, Field, validators
from typing import List, Optional
from datetime import datetime

class BusBase(BaseModel):
    """Base bus schemas with common fields"""
    bus_number: str = Field(..., max_length=20, description="Unique bus number")
    license_plate: str = Field(..., max_length=15, description="License plate of the bus")
    capacity: int = Field(..., gt=0, description="Seating capacity of the bus")
    model: Optional[str] = Field(None, max_length=50, description="Model of the bus")
    year: Optional[int] = Field(None, ge=1900, le=datetime.now().year, description="Manufacturing year of the bus")
    is_active: bool = Field(default=True, description="Indicates if the bus is active")
    current_route_id: Optional[int] = Field(None, description="ID of the current route assigned to the bus")
    current_driver_id: Optional[int] = Field(None, description="ID of the current driver assigned to the bus")  

class BusCreate(BusBase):
    """Schema for creating a new bus"""
    current_route_id: Optional[int] = Field(None, descrition="Initial route assignment")

    @validators('bus_number')
    def validate_bus_number(self, cls, v):
        # Ensure bus number follows a specific format, (e.g., BRT-001, BUS001)
        if not v.replace("-", "").replace('_', '').isalnum():
            raise ValueError("Bus number must contain only letters, numbers, hyphens, and underscores")
        return v.upper()