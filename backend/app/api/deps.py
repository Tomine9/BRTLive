"""
Extra helper functions for API endpoints
Use these when you need common validations
"""
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.models.bus import Bus
from app.models.driver import Driver
from app.models.route import Route
from app.models.terminal import Terminal

# Get or 404 helpers
async def get_bus_or_404(
    bus_id: int,
    db: AsyncSession = Depends(get_db)
) -> Bus:
    """Get bus or throw 404 error"""
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    return bus

async def get_driver_or_404(
    driver_id: int,
    db: AsyncSession = Depends(get_db)
) -> Driver:
    """Get driver or throw 404 error"""
    result = await db.execute(select(Driver).filter(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return driver

async def get_route_or_404(
    route_id: int,
    db: AsyncSession = Depends(get_db)
) -> Route:
    """Get route or throw 404 error"""
    result = await db.execute(select(Route).filter(Route.id == route_id))
    route = result.scalar_one_or_none()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    return route

async def get_terminal_or_404(
    terminal_id: int,
    db: AsyncSession = Depends(get_db)
) -> Terminal:
    """Get terminal or throw 404 error"""
    result = await db.execute(select(Terminal).filter(Terminal.id == terminal_id))
    terminal = result.scalar_one_or_none()
    
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")
    
    return terminal

# Pagination helper
class Pagination:
    """Simple pagination for lists"""
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Skip records"),
        limit: int = Query(100, ge=1, le=1000, description="Max records")
    ):
        self.skip = skip
        self.limit = limit