from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.dependencies import get_db, require_driver, get_current_active_user
from app.schemas.tracking import LocationUpdate, TrackingResponse
from app.models.tracking import BusTracking as Tracking
from app.models.bus import Bus
from app.models.user import User
from app.core.websocket import manager

router = APIRouter(prefix="/tracking", tags=["Tracking"])

@router.post("/update-location")
async def update_location(
    location: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    driver: User = Depends(require_driver)
):
    """Driver updates bus location"""
    
    # Check bus exists
    result = await db.execute(select(Bus).filter(Bus.id == location.bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    # Save location
    tracking = Tracking(
        bus_id=location.bus_id,
        latitude=location.latitude,
        longitude=location.longitude,
        speed=location.speed,
        heading=location.heading,
        timestamp=datetime.now(tz=timezone.utc)
    )
    
    db.add(tracking)
    await db.commit()
    await db.refresh(tracking)
    
    # Send to WebSocket clients
    await manager.broadcast({
        "type": "location_update",
        "bus_id": location.bus_id,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "speed": location.speed,
        "timestamp": tracking.gps_timestamp.isoformat()
    })
    
    return {"message": "Location updated"}

@router.get("/bus/{bus_id}/current")
async def get_current_location(
    bus_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get bus current location"""
    
    query = select(Tracking)\
        .filter(Tracking.bus_id == bus_id)\
        .order_by(Tracking.gps_timestamp.desc())\
        .limit(1)
    
    result = await db.execute(query)
    tracking = result.scalar_one_or_none()
    
    if not tracking:
        raise HTTPException(status_code=404, detail="No location data")
    
    return tracking

@router.get("/bus/{bus_id}/history")
async def get_location_history(
    bus_id: int,
    hours: int = 24,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get bus location history"""

    time_ago = datetime.now(timezone.utc) - timedelta(hours=hours)

    query = select(Tracking)\
        .filter(Tracking.bus_id == bus_id)\
        .filter(Tracking.gps_timestamp >= time_ago)\
        .order_by(Tracking.gps_timestamp.desc())
    
    result = await db.execute(query)
    history = result.scalars().all()
    
    return history

@router.get("/active-buses")
async def get_active_buses(db: AsyncSession = Depends(get_db)):
    """Get all buses that moved in last 10 minutes"""

    time_ago = datetime.now(timezone.utc) - timedelta(minutes=10)

    query = select(Tracking.bus_id)\
        .filter(Tracking.gps_timestamp >= time_ago)\
        .distinct()
    
    result = await db.execute(query)
    bus_ids = [row[0] for row in result.all()]
    
    # Get bus details
    if bus_ids:
        buses_query = select(Bus).filter(Bus.id.in_(bus_ids))
        buses_result = await db.execute(buses_query)
        buses = buses_result.scalars().all()
        return buses
    
    return []

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time location updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)