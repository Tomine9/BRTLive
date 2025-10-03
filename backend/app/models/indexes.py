from sqlalchemy import Index
from .bus import Bus
from .routeStop import RouteStop
from .BusArrivalPrediction import BusArrivalPrediction
from .BusAssignment import BusAssignment
from .tracking import BusTracking

all_indexes = [
    Index('idy_tracking_bus_updated', BusTracking.bus_id, BusTracking.last_updated),
    Index('idy_bus_route_active', Bus.route_id, Bus.is_active),
    Index('idy_bus_assignments_active', BusAssignment.is_active, BusAssignment.start_shift),
    Index('idy_arrival_preditions_terminal_time', BusArrivalPrediction.terminal_id, BusArrivalPrediction.estimated_arrival_time),
    Index('idy_route_stops_order', RouteStop.route_id, RouteStop.stop_order)
]