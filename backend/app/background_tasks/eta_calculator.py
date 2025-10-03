# =============================================================================
# Essential ETA Calculator - Simple & Concise
# =============================================================================

import asyncio
import logging
from datetime import datetime, timedelta, timezone
import sqlalchemy.exc
from sqlalchemy.orm import Session
from sqlalchemy import and_, select

from app.database import async_session
from app.models.bus import Bus
from app.models.driver import Driver
from app.models.eta import ETAPrediction
from app.services.eta_service import ETAService
from app.core.websocket import websocket_manager

logger = logging.getLogger(__name__)

class ETACalculator:
    def __init__(self):
        self.is_running = False
        self.stats = {
            'buses_processed': 0,
            'predictions_made': 0,
            'errors': 0,
            'status': 'stopped'
        }
    
    async def start(self):
        """Main loop - runs every 60 seconds"""
        self.is_running = True
        self.stats['status'] = 'running'
        
        logger.info("🚀 ETA Calculator started")
        
        while self.is_running:
            try:
                await self._calculate_etas()
                await asyncio.sleep(60)  # Wait 1 minute
                
            except (asyncio.TimeoutError, ConnectionError, asyncio.CancelledError) as e:
                logger.error("ETA calculation error: %s", e)
                self.stats['errors'] += 1
                await asyncio.sleep(60)
    
    async def _calculate_etas(self):
        """Calculate ETAs for all active buses"""

        async with async_session() as db:
            try:
                # 1. Get active buses
                buses = await db.execute(
                    select(Bus).join(Driver).filter(
                        and_(
                    Bus.is_active,
                    Driver.is_on_duty,
                    Bus.current_route_id.isnot(None)
                    )
                ).all()
                )
                if not buses:
                    logger.info("No active buses found for ETA calculation")
                    self.stats['status'] = 'idle'
                    return
                
                # 2. Calculate ETA for each bus
                eta_service = ETAService(db)
                total_predictions = 0
                successful_buses = 0
                
                for bus in buses:
                    try:
                        # Calculate predictions
                        predictions = await eta_service.calculate_eta_for_bus(bus.id)
                        
                        if predictions:
                            # Save predictions
                            await eta_service.store_eta_predictions(predictions)
                            total_predictions += len(predictions)
                            successful_buses += 1
                            
                            logger.debug("Bus %d: %s ETAs", bus.id, len(predictions))
                    
                    except(sqlalchemy.exc.SQLAlchemyError, ValueError) as e:
                        logger.error("Bus %d failed: %s", bus.id, e)
                        continue
                
                # 3. Send updates to dashboards
                await self._send_updates(db)
                
                # 4. Update stats
                self.stats['buses_processed'] = successful_buses
                self.stats['predictions_made'] = total_predictions
                self.stats['status'] = 'healthy'
                
                logger.info("✅ Processed %d/%s buses,%d predictions", successful_buses, len(buses), total_predictions)
                
            except (sqlalchemy.exc.SQLAlchemyError, ConnectionError, TimeoutError) as e:
                logger.error("ETA calculation failed: %s", e)
                self.stats['status'] = 'error'
            finally:
                db.close()
    
    async def _send_updates(self, db: Session):
        """Send ETA updates to dashboards"""
        
        try:
            # Get recent predictions (last 2 minutes)
            recent_etas = db.query(ETAPrediction).filter(
                ETAPrediction.calculated_at >= datetime.now(timezone.utc) - timedelta(minutes=2)
            ).all()
            
            if not recent_etas:
                return
            
            # Group by bus stop
            stops = {}
            for eta in recent_etas:
                stop_id = eta.stop_id
                if stop_id not in stops:
                    stops[stop_id] = []
                
                stops[stop_id].append({
                    'bus_number': eta.bus.bus_number if eta.bus else 'Unknown',
                    'minutes_until_arrival': eta.minutes_until_arrival,
                    'confidence': eta.confidence_score
                })
            
            # Send to each terminal
            for stop_id, etas in stops.items():
                message = {
                    'type': 'eta_update',
                    'stop_id': stop_id,
                    'etas': etas,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                await websocket_manager.broadcast_to_terminal(message, stop_id)
            
            logger.debug("📡 Sent updates to %d terminals", len(stops))
            
        except (sqlalchemy.exc.SQLAlchemyError, ConnectionError) as e:
            logger.error("Failed to send updates: %s", e)
    
    def get_stats(self):
        """Get current statistics"""
        return self.stats.copy()
    
    def stop(self):
        """Stop the calculator"""
        self.is_running = False
        self.stats['status'] = 'stopped'
        logger.info("🛑 ETA Calculator stopped")

# Create global instance
eta_calculator = ETACalculator()

# =============================================================================
# USAGE
# =============================================================================

"""
Start the calculator:
    asyncio.create_task(eta_calculator.start())

What it does:
    1. Every 60 seconds, finds all active buses
    2. Calculates ETA predictions for each bus
    3. Saves predictions to database  
    4. Sends updates to terminal dashboards
    5. Logs progress and errors

Check status:
    stats = eta_calculator.get_stats()
    # Returns: {'buses_processed': 45, 'predictions_made': 180, 'status': 'healthy'}

Stop it:
    eta_calculator.stop()
"""