# =============================================================================
# Simple BRTLive Analytics - Essential Code Only
# =============================================================================

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, distinct

from app.database import async_session
from app.models.bus import Bus
from app.models.tracking import BusTracking
from app.core.websocket import websocket_manager

logger = logging.getLogger(__name__)

class SimpleAnalytics:
    def __init__(self):
        self.is_running = False
    
    async def start(self):
        """Run analytics every hour"""
        self.is_running = True
        
        while self.is_running:
            try:
                await self._process_metrics()
                await asyncio.sleep(3600)  # Wait 1 hour
            except Exception as e:
                logger.error("Analytics error: %s", e)
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _process_metrics(self):
        """Calculate and broadcast basic metrics"""
        
        async with async_session() as db:
            try:
                # 1. Count active buses (GPS data in last 10 minutes)
                ten_min_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
                
                result = await db.execute(
                    select(func.count(distinct(BusTracking.bus_id)))
                    .filter(BusTracking.gps_timestamp >= ten_min_ago)
                )
                active_buses = result.scalar() or 0
                
                # 2. Total active buses in system
                result = await db.execute(
                    select(func.count(Bus.id))
                    .filter(Bus.is_active)
                )
                total_buses = result.scalar() or 0
                
                # 3. Average speed (last hour, filter bad data)
                one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
                
                result = await db.execute(
                    select(func.avg(BusTracking.speed_km))
                    .filter(
                        BusTracking.gps_timestamp >= one_hour_ago,
                        BusTracking.speed_km > 0,
                        BusTracking.speed_km < 100
                    )
                )
                avg_speed = result.scalar() or 0
                
                # 4. GPS updates count (last hour)
                result = await db.execute(
                    select(func.count(BusTracking.id))
                    .filter(BusTracking.gps_timestamp >= one_hour_ago)
                )
                gps_updates = result.scalar() or 0
                
                # 5. Create metrics
                metrics = {
                    'type': 'analytics_update',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'data': {
                        'active_buses': active_buses,
                        'total_buses': total_buses,
                        'fleet_utilization': round((active_buses / total_buses * 100) if total_buses > 0 else 0, 1),
                        'average_speed_kmh': round(float(avg_speed), 1),
                        'gps_updates_last_hour': gps_updates
                    }
                }
                
                # 6. Send to dashboards
                await websocket_manager.broadcast_all(metrics)
                
                logger.info(
                    "Analytics: %d/%d buses active, %.1f%% utilization, %.1f km/h avg",
                    active_buses, total_buses,
                    round((active_buses / total_buses * 100) if total_buses > 0 else 0, 1),
                    round(float(avg_speed), 1)
                )

            except (asyncio.TimeoutError, ConnectionError) as e:
                logger.error("Metrics processing failed: %s", e)
    
    def stop(self):
        """Stop analytics processing"""
        self.is_running = False

# Global instance
analytics = SimpleAnalytics()

# =============================================================================
# USAGE
# =============================================================================

"""
Start analytics:
    asyncio.create_task(analytics.start())

What it does:
    - Counts active buses every hour
    - Calculates average speed  
    - Counts GPS updates
    - Sends updates to dashboards

Dashboard gets:
    {
        "active_buses": 47,
        "total_buses": 50,
        "fleet_utilization": 94.0,
        "average_speed_kmh": 25.3,
        "gps_updates_last_hour": 2847
    }
"""