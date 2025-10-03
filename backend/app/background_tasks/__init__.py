"""
Background Task Module - Simple and Clean Implementation
"""

from .analytics_aggregator import SimpleAnalytics
from .data_cleanup import DataCleanupService
from .location_updater import LocationUpdater
from .eta_calculator import ETACalculator

# Main task manager instance
simple_analytics = SimpleAnalytics()
data_cleanup_service = DataCleanupService()
location_updater = LocationUpdater()
eta_calculator = ETACalculator()

# Export the important stuff
__all__ = [
    'simple_analytics',
    'data_cleanup_service',
    'location_updater',
    'eta_calculator'
]