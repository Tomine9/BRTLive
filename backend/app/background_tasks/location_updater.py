import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.bus import Bus
from app.models.tracking import BusTracking
from app.core.websocket import websocket_manager
from app.services.dashboard_service import DashboardService


class LocationUpdater:
    def __init__(self):
        self.db = SessionLocal()
    
    async def start_periodic_updates(self, interval: int = 30):
        """Start periodic location updates and dashboard broadcasts"""
        while True:
            try:
                await self.update_bus_locations()
                await self.broadcast_dashboard_updates()
                await asyncio.sleep(interval)
            except Exception as e:
                print(f"Error in location updater: {e}")
                await asyncio.sleep(interval)
    
    async def update_bus_locations(self):
        """Process location updates from mobile apps"""
        # This would typically receive GPS data from driver mobile apps
        # via API endpoints and store in BusTracking table
        pass
    
    async def broadcast_dashboard_updates(self):
        """Broadcast real-time updates to dashboard subscribers"""
        try:
            dashboard_service = DashboardService(self.db)
            
            # Get all terminals and broadcast their updates
            terminals = self.db.query(Terminal).all()
            
            for terminal in terminals:
                dashboard_data = await dashboard_service.get_terminal_dashboard(terminal.id)
                await websocket_manager.broadcast_to_terminal(
                    {
                        "type": "dashboard_update",
                        "data": dashboard_data.dict()
                    },
                    terminal.id
                )
        except Exception as e:
            print(f"Error broadcasting dashboard updates: {e}")


# Background task instance
location_updater = LocationUpdater()