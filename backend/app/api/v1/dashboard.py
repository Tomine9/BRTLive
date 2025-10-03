from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from datetime import datetime, timedelta, timezone

from app.dependencies import get_db, get_current_active_user
from app.models.bus import Bus
from app.models.driver import Driver
from app.models.route import Route
from app.models.terminal import Terminal
from app.models.tracking import BusTracking as Tracking
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard numbers"""
    
    # Count everything
    result = await db.execute(select(func.count()).select_from(Bus))
    total_buses = result.scalar() or 0
    
    result = await db.execute(select(func.count()).select_from(Bus).filter(Bus.is_active))
    active_buses = result.scalar() or 0
    
    result = await db.execute(select(func.count()).select_from(Driver))
    total_drivers = result.scalar() or 0
    
    result = await db.execute(select(func.count()).select_from(Driver).filter(Driver.is_available))
    available_drivers = result.scalar() or 0
    
    result = await db.execute(select(func.count()).select_from(Route))
    total_routes = result.scalar() or 0
    
    result = await db.execute(select(func.count()).select_from(Terminal))
    total_terminals = result.scalar() or 0
    
    # Count buses that moved in last 10 minutes
    time_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
    result = await db.execute(
        select(func.count(distinct(Tracking.bus_id)))
        .filter(Tracking.gps_timestamp >= time_ago)
    )
    buses_online = result.scalar() or 0
    
    return {
        "total_buses": total_buses or 0,
        "active_buses": active_buses or 0,
        "buses_online": buses_online or 0,
        "total_drivers": total_drivers or 0,
        "available_drivers": available_drivers or 0,
        "total_routes": total_routes or 0,
        "total_terminals": total_terminals or 0
    }

@router.get("/map")
async def get_map_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all data for map view"""

    time_ago = datetime.now(timezone.utc) - timedelta(minutes=10)

    # Get active buses
    buses_result = await db.execute(select(Bus).filter(Bus.is_active))
    active_buses = buses_result.scalars().all()
    
    # Get latest location for each bus
    buses_data = []
    for bus in active_buses:
        location_query = select(Tracking)\
            .filter(Tracking.bus_id == bus.id)\
            .filter(Tracking.timestamp >= time_ago)\
            .order_by(Tracking.timestamp.desc())\
            .limit(1)
        
        location_result = await db.execute(location_query)
        location = location_result.scalar_one_or_none()
        
        if location:
            buses_data.append({
                "bus_id": bus.id,
                "plate_number": bus.plate_number,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "speed": location.speed
            })
    
    # Get all terminals
    terminals_result = await db.execute(select(Terminal))
    terminals = terminals_result.scalars().all()
    
    terminals_data = [
        {
            "id": t.id,
            "name": t.name,
            "latitude": t.latitude,
            "longitude": t.longitude
        }
        for t in terminals
    ]
    
    return {
        "buses": buses_data,
        "terminals": terminals_data
    }