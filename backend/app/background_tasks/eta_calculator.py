# =============================================================================
# BRTLive ETA Calculator - Essential Basics
# =============================================================================

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import and_
from contextlib import asynccontextmanager

from app.database import SessionLocal
from app.models.bus import Bus
from app.models.driver import Driver
from app.models.eta import ETAPrediction
from app.services.eta_service import ETAService
from app.core.websocket import websocket_manager
from app.config import settings

# =============================================================================
# 1. BASIC ERROR CLASSES - Just the essential ones
# =============================================================================

class ETAError(Exception):
    """Base ETA error - keeps it simple"""
    def __init__(self, message: str, bus_id: int = None):
        self.message = message
        self.bus_id = bus_id
        self.timestamp = datetime.now(timezone.utc)
        super().__init__(message)

# =============================================================================
# 2. BASIC METRICS - Track what matters most
# =============================================================================

class BasicMetrics:
    """Simple metrics tracking"""
    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
        self.buses_found = 0
        self.buses_success = 0
        self.buses_failed = 0
        self.predictions_made = 0
        self.errors = []
    
    @property
    def success_rate(self) -> float:
        if self.buses_found == 0:
            return 0.0
        return (self.buses_success / self.buses_found) * 100
    
    @property
    def processing_time(self) -> float:
        return (datetime.now(timezone.utc) - self.start_time).total_seconds()

# =============================================================================
# 3. SIMPLIFIED ETA CALCULATOR - Core functionality only
# =============================================================================

class SimpleETACalculator:
    """Simplified ETA Calculator with essential improvements"""
    
    def __init__(self):
        # Basic settings
        self.calculation_interval = 60  # seconds
        self.timeout = 50  # max calculation time
        self.max_failures = 3  # consecutive failures before alert
        
        # State tracking
        self.is_running = False
        self.consecutive_failures = 0
        self.logger = logging.getLogger("brtlive.eta")
        
        # Simple stats
        self.stats = {
            'total_calculations': 0,
            'successful_calculations': 0,
            'total_buses_processed': 0,
            'total_predictions_made': 0,
            'last_success_time': None,
            'system_status': 'unknown'  # healthy, degraded, critical
        }
    
    # =========================================================================
    # MAIN LOOP - Enhanced but simplified
    # =========================================================================
    
    async def start_periodic_calculations(self):
        """Main calculation loop with basic error handling"""
        
        self.is_running = True
        self.logger.info("Starting ETA Calculator (interval: %ds)", self.calculation_interval)
        
        while self.is_running:
            metrics = BasicMetrics()
            
            try:
                # Run calculation with timeout protection
                await asyncio.wait_for(
                    self._run_calculation_cycle(metrics),
                    timeout=self.timeout
                )
                
                # Success - reset failure counter
                self.consecutive_failures = 0
                self.stats['successful_calculations'] += 1
                self.stats['last_success_time'] = datetime.now(timezone.utc)
                self.stats['system_status'] = 'healthy'
                
                self.logger.info(
                    "ETA cycle completed: %d/%d buses, %d predictions, %.1fs",
                    metrics.buses_success, metrics.buses_found,
                    metrics.predictions_made, metrics.processing_time
                )
                
            except asyncio.TimeoutError:
                await self._handle_timeout(metrics)
                
            except ETAError as e:
                await self._handle_eta_error(e, metrics)
                
            except (sqlalchemy.exc.SQLAlchemyError, ConnectionError) as e:
                await self._handle_unexpected_error(e, metrics)
                
            except ValueError as e:
                await self._handle_unexpected_error(e, metrics)
            
            finally:
                # Always update stats and wait
                self._update_stats(metrics)
                await asyncio.sleep(self.calculation_interval)
    
    async def _run_calculation_cycle(self, metrics: BasicMetrics):
        """Single calculation cycle"""
        
        # Step 1: Calculate ETAs for all buses
        await self._calculate_all_etas(metrics)
        
        # Step 2: Broadcast updates to dashboards
        await self._broadcast_updates()
    
    # =========================================================================
    # ETA CALCULATION - Core logic with better error handling
    # =========================================================================
    
    async def _calculate_all_etas(self, metrics: BasicMetrics):
        """Calculate ETAs with improved error handling"""
        
        async with self._get_db_session() as db:
            eta_service = ETAService(db)
            
            # Get active buses
            active_buses = self._get_active_buses(db)
            metrics.buses_found = len(active_buses)
            
            if not active_buses:
                self.logger.warning("No active buses found")
                return
            
            self.logger.info("Processing %d active buses", len(active_buses))
            
            # Process each bus
            for bus in active_buses:
                try:
                    await self._process_single_bus(bus, eta_service, metrics)
                    
                except ETAError as e:
                    metrics.buses_failed += 1
                    metrics.errors.append(f"Bus {bus.id}: {e.message}")
                    self.logger.error("Bus %s failed: %s", bus.bus_number, e.message)
                    continue  # Skip this bus, continue with others
                
                except (sqlalchemy.exc.SQLAlchemyError, ValueError, ConnectionError) as e:
                    metrics.buses_failed += 1
                    metrics.errors.append(f"Bus {bus.id}: Database or calculation error")
                    self.logger.error("Bus %s error: %s", bus.bus_number, e)
                    continue
    
    def _get_active_buses(self, db: Session) -> List[Bus]:
        """Get active buses with basic error handling"""
        try:
            return db.query(Bus).join(Driver).filter(
                and_(
                    Bus.is_active,
                    Driver.is_on_duty,
                    Bus.current_route_id.isnot(None)
                )
            ).all()
        except Exception as e:
            raise ETAError(f"Failed to get active buses: {e}") from e
    
    async def _process_single_bus(self, bus: Bus, eta_service: ETAService, metrics: BasicMetrics):
        """Process one bus with retry logic"""
        
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            try:
                # Calculate predictions
                predictions = await eta_service.calculate_eta_for_bus(bus.id)
                
                if not predictions:
                    raise ETAError("No predictions generated", bus.id)
                
                # Store predictions
                success = await eta_service.store_eta_predictions(predictions)
                if not success:
                    raise ETAError("Failed to store predictions", bus.id)
                
                # Success!
                metrics.buses_success += 1
                metrics.predictions_made += len(predictions)
                
                self.logger.debug("Generated %d ETAs for bus %s", len(predictions), bus.bus_number)
                return
                
            except ETAError as e:
                if attempt < max_retries and "database" in e.message.lower():
                    # Retry database errors
                    self.logger.warning("Retrying bus %d (attempt %s)", bus.bus_number, attempt + 1)
                    await asyncio.sleep(1)
                    continue
                else:
                    # Max retries or non-retryable error
                    raise e
            
            except (sqlalchemy.exc.SQLAlchemyError, ValueError, ConnectionError, asyncio.TimeoutError) as e:
                if attempt < max_retries:
                    await asyncio.sleep(1)
                    continue
                else:
                    raise ETAError(f"Calculation failed: {e}", bus.id) from e
    
    # =========================================================================
    # BROADCASTING - Simplified but robust
    # =========================================================================
    
    async def _broadcast_updates(self):
        """Broadcast ETA updates to dashboards"""
        
        async with self._get_db_session() as db:
            try:
                # Get recent predictions
                recent_etas = db.query(ETAPrediction).filter(
                    ETAPrediction.calculated_at >= datetime.now(timezone.utc) - timedelta(minutes=2)
                ).all()
                
                if not recent_etas:
                    return
                
                # Group by stop
                stops_data = self._group_etas_by_stop(recent_etas)
                
                # Send to dashboards
                for stop_id, etas in stops_data.items():
                    message = {
                        'type': 'eta_update',
                        'stop_id': stop_id,
                        'etas': etas,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    
                    try:
                        await websocket_manager.broadcast_to_terminal(message, stop_id)
                    except Exception as e:
                        self.logger.error(f"Broadcast failed for stop {stop_id}: {e}")
                
                self.logger.info(f"Broadcasted to {len(stops_data)} terminals")
                
            except (sqlalchemy.exc.SQLAlchemyError, ConnectionError, ValueError) as e:
                raise ETAError(f"Broadcast failed: {e}")
    
    def _group_etas_by_stop(self, etas: List[ETAPrediction]) -> Dict[int, List[Dict]]:
        """Group ETAs by stop for broadcasting"""
        
        grouped = {}
        for eta in etas:
            stop_id = eta.stop_id
            if stop_id not in grouped:
                grouped[stop_id] = []
            
            grouped[stop_id].append({
                'bus_id': eta.bus_id,
                'bus_number': eta.bus.bus_number if eta.bus else 'Unknown',
                'minutes_until_arrival': eta.minutes_until_arrival,
                'confidence': eta.confidence_score
            })
        
        return grouped
    
    # =========================================================================
    # ERROR HANDLING - Simplified but effective
    # =========================================================================
    
    async def _handle_timeout(self, metrics: BasicMetrics):
        """Handle calculation timeout"""
        
        self.consecutive_failures += 1
        
        self.logger.error(
            f"ETA calculation timed out after {self.timeout}s "
            f"(consecutive failures: {self.consecutive_failures})"
        )
        
        if self.consecutive_failures >= self.max_failures:
            await self._trigger_alert("TIMEOUT")
    
    async def _handle_eta_error(self, error: ETAError, metrics: BasicMetrics):
        """Handle ETA-specific errors"""
        
        self.consecutive_failures += 1
        
        self.logger.error(
            f"ETA calculation error: {error.message} "
            f"(consecutive failures: {self.consecutive_failures})"
        )
        
        if self.consecutive_failures >= self.max_failures:
            await self._trigger_alert("CALCULATION_ERROR")
    
    async def _handle_unexpected_error(self, error: Exception, metrics: BasicMetrics):
        """Handle unexpected errors"""
        
        self.consecutive_failures += 1
        
        self.logger.error(
            f"Unexpected ETA error: {error} "
            f"(consecutive failures: {self.consecutive_failures})"
        )
        
        if self.consecutive_failures >= self.max_failures:
            await self._trigger_alert("UNEXPECTED_ERROR")
    
    async def _trigger_alert(self, alert_type: str):
        """Trigger alert for critical issues"""
        
        self.stats['system_status'] = 'critical'
        
        self.logger.critical(
            f"🚨 CRITICAL: ETA system failure - {alert_type} "
            f"(failures: {self.consecutive_failures})"
        )
        
        # TODO: Add external alerting (email, SMS, Slack)
        # await send_alert_email("ETA system down", alert_type)
        # await send_slack_message(f"🚨 ETA system failure: {alert_type}")
    
    # =========================================================================
    # UTILITIES - Helper methods
    # =========================================================================
    
    @asynccontextmanager
    async def _get_db_session(self):
        """Simple database session manager"""
        db = SessionLocal()
        try:
            yield db
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
    
    def _update_stats(self, metrics: BasicMetrics):
        """Update system statistics"""
        
        self.stats['total_calculations'] += 1
        self.stats['total_buses_processed'] += metrics.buses_success
        self.stats['total_predictions_made'] += metrics.predictions_made
        
        # Update system status based on success rate
        if metrics.success_rate >= 90:
            self.stats['system_status'] = 'healthy'
        elif metrics.success_rate >= 70:
            self.stats['system_status'] = 'degraded'
        else:
            self.stats['system_status'] = 'critical'
    
    # =========================================================================
    # PUBLIC METHODS - Keep the same interface
    # =========================================================================
    
    async def calculate_eta_for_single_bus(self, bus_id: int) -> List[ETAPrediction]:
        """Calculate ETA for specific bus (on-demand)"""
        
        async with self._get_db_session() as db:
            try:
                eta_service = ETAService(db)
                predictions = await eta_service.calculate_eta_for_bus(bus_id)
                
                if predictions:
                    await eta_service.store_eta_predictions(predictions)
                
                return predictions or []
                
            except Exception as e:
                self.logger.error("Single bus ETA failed for bus %d: %s", bus_id, e)
                raise ETAError(f"Single bus calculation failed: {e}", bus_id) from e
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        
        uptime = (datetime.now(timezone.utc) - self.stats.get('uptime_start', datetime.now(timezone.utc))).total_seconds()
        
        return {
            **self.stats,
            'uptime_hours': uptime / 3600,
            'consecutive_failures': self.consecutive_failures,
            'is_running': self.is_running,
            'calculation_interval': self.calculation_interval
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Get simple health check"""
        
        return {
            'status': self.stats['system_status'],
            'is_running': self.is_running,
            'consecutive_failures': self.consecutive_failures,
            'last_success': self.stats.get('last_success_time'),
            'needs_attention': self.consecutive_failures >= self.max_failures
        }
    
    def stop(self):
        """Stop the calculator"""
        self.is_running = False
        self.logger.info("ETA Calculator stopped")

# =============================================================================
# 4. USAGE - Drop-in replacement for your existing code
# =============================================================================

# Create instance (replaces your existing ETACalculator)
eta_calculator = SimpleETACalculator()

# Integration example
async def start_background_tasks():
    """Start the ETA calculator as a background task"""
    
    # This replaces your existing start call
    await eta_calculator.start_periodic_calculations()

# Health check endpoint example
async def health_check():
    """API endpoint for health checking"""
    
    health = eta_calculator.get_health()
    
    if health['status'] == 'critical':
        return {"status": "unhealthy", "details": health}, 503
    elif health['status'] == 'degraded':
        return {"status": "degraded", "details": health}, 200
    else:
        return {"status": "healthy", "details": health}, 200

# =============================================================================
# 5. INTEGRATION WITH YOUR EXISTING CODE
# =============================================================================

# In your main.py - replace existing eta_calculator import:
# from app.background_tasks.eta_calculator import eta_calculator

# The interface remains the same:
# - eta_calculator.start_periodic_calculations()
# - eta_calculator.get_statistics() 
# - eta_calculator.calculate_eta_for_single_bus(bus_id)
# - eta_calculator.stop()

# But now you get:
# ✅ Better error handling and recovery
# ✅ Timeout protection (won't hang forever)
# ✅ Automatic retry for recoverable errors  
# ✅ System health monitoring
# ✅ Detailed logging with context
# ✅ Performance metrics tracking