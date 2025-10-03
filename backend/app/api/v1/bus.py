from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.dependencies import get_db, require_admin, get_current_active_user
from app.schemas.bus import BusCreate, BusUpdate, BusResponse
from app.models.bus import Bus
from app.models.user import User

router = APIRouter(prefix="/buses", tags=["Buses"])

@router.get("/", response_model=List[BusResponse])
async def get_buses(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all buses"""
    query = select(Bus)
    
    if is_active is not None:
        query = query.filter(Bus.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{bus_id}", response_model=BusResponse)
async def get_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get single bus"""
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    return bus

@router.post("/", response_model=BusResponse, status_code=status.HTTP_201_CREATED)
async def create_bus(
    bus_data: BusCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create new bus"""
    
    # Check plate number exists
    result = await db.execute(
        select(Bus).filter(Bus.plate_number == bus_data.plate_number)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Plate number already exists")
    
    # Create bus
    new_bus = Bus(**bus_data.Dict())
    db.add(new_bus)
    await db.commit()
    await db.refresh(new_bus)
    
    return new_bus

@router.put("/{bus_id}", response_model=BusResponse)
async def update_bus(
    bus_id: int,
    bus_data: BusUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update bus"""
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    # Update fields
    for field, value in bus_data.dict(exclude_unset=True).items():
        setattr(bus, field, value)
    
    await db.commit()
    await db.refresh(bus)
    
    return bus

@router.delete("/{bus_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete bus"""
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    await db.delete(bus)
    await db.commit()

@router.patch("/{bus_id}/activate")
async def activate_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Turn bus on"""
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    bus.is_active
    await db.commit()
    
    return {"message": "Bus activated"}

@router.patch("/{bus_id}/deactivate")
async def deactivate_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Turn bus off"""
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    bus.is_active is False
    await db.commit()
    
    return {"message": "Bus deactivated"}