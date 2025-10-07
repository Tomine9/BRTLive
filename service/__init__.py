from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class BusLocation(BaseModel):
    bus_id: str
    driver_phone: str
    latitude: float
    longitude: float
    timestamp: datetime = Field(default_factory=datetime.now)
    speed: float = 0.0


class Bus(BaseModel):
    bus_id: str
    driver_phone: str
    driver_name: str
    plate_number: str
    capacity: int
    current_terminal: Optional[str] = None
    status: str = "available"
    last_location: Optional[BusLocation] = None


class Terminal(BaseModel):
    terminal_id: str
    name: str
    latitude: float
    longitude: float
    total_capacity: int
    buses_present: List[str] = Field(default_factory=list)


class WaitTimeEstimate(BaseModel):
    terminal_id: str
    buses_available: int
    estimated_wait_minutes: int
    next_bus_arrival: Optional[datetime] = None


class BusTrackingService:
    def __init__(self):
        self.buses: Dict[str, Bus] = {}
        self.terminals: Dict[str, Terminal] = {}
        self.location_history: Dict[str, List[BusLocation]] = {}
        
    def register_bus(self, bus: Bus) -> Dict:
        self.buses[bus.bus_id] = bus
        self.location_history[bus.bus_id] = []
        return {"message": f"Bus {bus.bus_id} registered", "bus": bus}
    
    def register_terminal(self, terminal: Terminal) -> Dict:
        self.terminals[terminal.terminal_id] = terminal
        return {"message": f"Terminal {terminal.name} registered", "terminal": terminal}
    
    def update_bus_location(self, bus_id: str, location: BusLocation) -> Dict:
        if bus_id not in self.buses:
            return {"error": "Bus not found"}
        
        if bus_id not in self.location_history:
            self.location_history[bus_id] = []
        self.location_history[bus_id].append(location)
        
        if len(self.location_history[bus_id]) > 100:
            self.location_history[bus_id] = self.location_history[bus_id][-100:]
        
        self.buses[bus_id].last_location = location
        self._check_terminal_presence(bus_id, location)
        
        return {"message": "Location updated", "bus_id": bus_id}
    
    def _check_terminal_presence(self, bus_id: str, location: BusLocation):
        RADIUS = 0.001  
        
        for tid, terminal in self.terminals.items():
            dist = ((location.latitude - terminal.latitude) ** 2 + 
                   (location.longitude - terminal.longitude) ** 2) ** 0.5
            
            if dist <= RADIUS:
                if bus_id not in terminal.buses_present:
                    terminal.buses_present.append(bus_id)
                    self.buses[bus_id].current_terminal = tid
                    self.buses[bus_id].status = "available"
            else:
                if bus_id in terminal.buses_present:
                    terminal.buses_present.remove(bus_id)
                    if self.buses[bus_id].current_terminal == tid:
                        self.buses[bus_id].current_terminal = None
                        self.buses[bus_id].status = "in_transit"
    
    def get_terminal_dashboard(self, terminal_id: str) -> Dict:
        if terminal_id not in self.terminals:
            return {"error": "Terminal not found"}
        
        terminal = self.terminals[terminal_id]
        buses = [self.buses[bid] for bid in terminal.buses_present if bid in self.buses]
        wait = self._calc_wait_time(terminal_id)
        
        return {
            "terminal": terminal,
            "buses_available": len(buses),
            "buses": buses,
            "wait_estimate": wait,
            "capacity_utilization": len(buses) / terminal.total_capacity * 100
        }
    
    def get_all_terminals_dashboard(self) -> List[Dict]:
        return [self.get_terminal_dashboard(tid) for tid in self.terminals.keys()]
    
    def _calc_wait_time(self, terminal_id: str) -> WaitTimeEstimate:
        terminal = self.terminals[terminal_id]
        available = len(terminal.buses_present)
        
        if available > 0:
            wait = 2
        else:
            incoming = self._get_incoming_buses(terminal_id)
            wait = min([b['eta'] for b in incoming]) if incoming else 15
        
        next_time = datetime.now() + timedelta(minutes=wait) if wait > 2 else None
        
        return WaitTimeEstimate(
            terminal_id=terminal_id,
            buses_available=available,
            estimated_wait_minutes=wait,
            next_bus_arrival=next_time
        )
    
    def _get_incoming_buses(self, terminal_id: str)  List[Dict]:
        incoming = []
        terminal = self.terminals[terminal_id]
        
        for bid, bus in self.buses.items():
            if bus.status == "in_transit" and bus.last_location:
                dist = ((bus.last_location.latitude - terminal.latitude) ** 2 + 
                       (bus.last_location.longitude - terminal.longitude) ** 2) ** 0.5
                dist_km = dist * 111
                speed = bus.last_location.speed if bus.last_location.speed > 0 else 30
                eta = int((dist_km / speed) * 60)
                
                if eta < 30:
                    incoming.append({"bus_id": bid, "eta": eta, "distance_km": round(dist_km, 2)})
        
        return sorted(incoming, key=lambda x: x['eta'])
    
    def get_bus_by_phone(self, phone: str) -> Optional[Bus]:
        for bus in self.buses.values():
            if bus.driver_phone == phone:
                return bus
        return None
    
    def get_all_buses(self) -> List[Bus]:
        return list(self.buses.values())


bus_tracking_service = BusTrackingService()