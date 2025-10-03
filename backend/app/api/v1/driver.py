from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.dependencies import get_db, require_admin, get_current_active_user
from app.schemas.driver import DriverCreate, DriverUpdate, DriverResponse
from app.models.driver import Driver
from app.models.bus import Bus
from app.models.user import User

router = APIRouter(prefix="/drivers", tags=["Drivers"])

@router.get("/", response_model=List[DriverResponse])
async def get_drivers(
    skip: int = 0,
    limit: int = 100,
    is_available: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all drivers"""
    query = select(Driver)
    if is_available is not None:
        query = query.filter(Driver.is_available == is_available)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get single driver"""
    result = await db.execute(select(Driver).filter(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(
    driver_data: DriverCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create new driver"""
    
    # Check license exists
    result = await db.execute(
        select(Driver).filter(Driver.license_number == driver_data.license_number)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="License number already exists")
    
    # Create driver
    new_driver = Driver(**driver_data.dict())
    db.add(new_driver)
    await db.commit()
    await db.refresh(new_driver)
    
    return new_driver

@router.put("/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: int,
    driver_data: DriverUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update driver"""
    result = await db.execute(select(Driver).filter(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Update fields
    for field, value in driver_data.dict(exclude_unset=True).items():
        setattr(driver, field, value)
    
    await db.commit()
    await db.refresh(driver)
    
    return driver

@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete driver"""
    result = await db.execute(select(Driver).filter(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    await db.delete(driver)
    await db.commit()

@router.patch("/{driver_id}/assign-bus/{bus_id}")
async def assign_bus(
    driver_id: int,
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Assign bus to driver"""
    
    # Get driver
    result = await db.execute(select(Driver).filter(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Get bus
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    # Assign
    driver.current_bus_id = bus_id
    driver.is_available = False
    await db.commit()
    
    return {"message": "Bus assigned successfully"}

@router.patch("/{driver_id}/unassign-bus")
async def unassign_bus(
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Remove bus from driver"""
    result = await db.execute(select(Driver).filter(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    driver.current_bus_id = None
    driver.is_available = True
    await db.commit()
    
    return {"message": "Bus unassigned successfully"}