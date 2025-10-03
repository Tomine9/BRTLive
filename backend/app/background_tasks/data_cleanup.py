"""
Data cleanup background task for BRTLive backend.
Handles cleanup of old tracking data, expired sessions, and analytics aggregation.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from sqlalchemy import delete, func

from app.database import get_db
from app.models.tracking import BusTracking as Tracking
from app.core.cache import _redis_client as redis_client
from app.config import settings

logger = logging.getLogger(__name__)


class DataCleanupService:
    """Centralized data cleanup service for BRT system."""
    
    def __init__(self):
        self.cleanup_config = {
            "tracking_retention_days": getattr(settings, "TRACKING_RETENTION_DAYS", 30),
            "cache_cleanup_pattern": "tracking:*",
            "batch_size": getattr(settings, "CLEANUP_BATCH_SIZE", 1000),
        }
    
    async def run_full_cleanup(self) -> Dict[str, Any]:
        """Execute all cleanup tasks and return summary."""
        logger.info("Starting data cleanup process...")
        start_time = datetime.now(timezone.utc)
        
        results = {
            "started_at": start_time,
            "tasks_completed": [],
            "errors": [],
            "total_records_cleaned": 0
        }
        
        cleanup_tasks = [
            ("tracking_data", self._cleanup_old_tracking_data),
            ("cache", self._cleanup_expired_cache),
            ("analytics_aggregation", self._aggregate_analytics_data)
        ]
        
        for task_name, task_func in cleanup_tasks:
            try:
                count = await task_func()
                results["tasks_completed"].append({
                    "task": task_name,
                    "records_processed": count,
                    "completed_at": datetime.now(timezone.utc)
                })
                results["total_records_cleaned"] += count
                logger.info("Completed %d: %s records processed", task_name, count)
            except (asyncio.CancelledError, ConnectionError, TimeoutError) as e:
                error_msg = f"Failed {task_name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                results["errors"].append(error_msg)
        
        duration = datetime.now(timezone.utc) - start_time
        results["duration_seconds"] = duration.total_seconds()
        results["completed_at"] = datetime.now(timezone.utc)

        logger.info("Data cleanup completed in %ds", duration.total_seconds().__round__(2))
        return results
    
    async def _cleanup_old_tracking_data(self) -> int:
        """Remove old tracking records beyond retention period."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(
            days=self.cleanup_config["tracking_retention_days"]
        )
        
        for db in get_db():
            try:
                # Delete in batches to avoid locking issues
                total_deleted = 0
                batch_size = self.cleanup_config["batch_size"]
                
                while True:
                    result = await db.execute(
                        delete(Tracking)
                        .where(Tracking.gps_timestamp < cutoff_date)
                        .limit(batch_size)
                    )
                    
                    deleted_count = result.rowcount()
                    if deleted_count == 0:
                        break
                    
                    total_deleted += deleted_count
                    await db.commit()
                    
                    # Small delay between batches
                    await asyncio.sleep(0.1)
                
                return total_deleted
                
            except Exception as e:
                await db.rollback()
                raise e
            finally:
                await db.close()
        return 0
    
    async def _cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries."""
        if not redis_client:
            return 0
        
        try:
            pattern = self.cleanup_config["cache_cleanup_pattern"]
            
            # Get all keys matching pattern
            keys = await redis_client.keys(pattern)
            
            if not keys:
                return 0
            
            # Remove expired keys
            expired_keys = []
            for key in keys:
                ttl = await redis_client.ttl(key)
                if ttl == -2:  # Key doesn't exist (expired)
                    expired_keys.append(key)
            
            if expired_keys:
                await redis_client.delete(*expired_keys)
            
            return len(expired_keys)

        except (asyncio.CancelledError, ConnectionError, TimeoutError) as e:
            logger.error("Cache cleanup failed: %s", e)
            return 0
    
    async def _aggregate_analytics_data(self) -> int:
        """Aggregate daily analytics data for reporting."""
        yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
        
        for db in get_db():
            try:
                # Example: Aggregate daily bus activity
                result = await db.execute(
                    db.func.count(Tracking.id)
                    .filter(
                        func.date(Tracking.gps_timestamp) == yesterday
                    )
                )
                
                daily_count = result.scalar() or 0
                
                # Store aggregated data (implement based on your analytics model)
                # This is a placeholder - implement according to your analytics schema
                logger.info("Aggregated %d tracking records for %s", daily_count, yesterday)
                
                await db.commit()
                return daily_count
                
            except Exception as e:
                await db.rollback()
                raise e
            finally:
                await db.close()
        return 0


# Background task functions for Celery/APScheduler integration
async def cleanup_old_data():
    """Main cleanup function to be called by background task scheduler."""
    cleanup_service = DataCleanupService()
    return await cleanup_service.run_full_cleanup()


async def cleanup_tracking_data_only():
    """Quick cleanup of just tracking data - for more frequent execution."""
    cleanup_service = DataCleanupService()
    count = await cleanup_service._cleanup_old_tracking_data()
    logger.info("Cleaned up %d old tracking records", count)
    return count


# Utility functions
def get_cleanup_schedule():
    """Return recommended cleanup schedule configuration."""
    return {
        "full_cleanup": "0 2 * * *",  # Daily at 2 AM
        "tracking_cleanup": "0 */6 * * *",  # Every 6 hours
        "cache_cleanup": "*/30 * * * *",  # Every 30 minutes
    }


if __name__ == "__main__":
    # For testing/manual execution
    async def test_cleanup():
        results = await cleanup_old_data()
        print(f"Cleanup completed: {results}")
    
    asyncio.run(test_cleanup())