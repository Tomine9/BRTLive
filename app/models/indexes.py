from sqlalchemy import Index
from .Bus import Bus
from .route import Route
from .routeStop import RouteStop
from .eta import Eta
from .BusAssignment import BusAssignment
from .tracking import Tracking
from .driver import Driver

all_indexes = [
    Index('idy_drivers_phone_number', Driver.phone_number),
    Index('idy_drivers_tracking_enabled', Driver.is_tracking_enabled, Driver.is_active),
    Index('idy_tracking_bus_id', Tracking.bus_id),
    Index('idy_tracking_last_updated', Tracking.last_updated),
    Index('tracking_driver_phone', Tracking.driver_phone_number),
    Index('idy_bus_route_active', Bus.route_id, Bus.is_active),
    Index('idy_bus_number_plate', Bus.plate_number),
    Index('idy_bus_assignments_active_bus', BusAssignment.is_active, BusAssignment.bus_id),
    Index('idy_bus_assignment_active_driver', BusAssignment.driver_id, BusAssignment.is_active),
    Index('idy_eta_terminal_time', Eta.terminal_id,Eta.estimated_arrival_time),
    Index('idy_eta_bus_active', Eta.is_active, Eta.bus_id),
    Index('idy_eta_active_updated', Eta.is_active, Eta.last_updated),
    Index('idy_route_stops_order', RouteStop.route_id, RouteStop.stop_order)
]