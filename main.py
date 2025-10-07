from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import uvicorn

from service import (
    bus_tracking_service,
    Bus, Terminal, BusLocation,
    WaitTimeEstimate

)

app = FastAPI(
    title="BRTLive API",
    description="Advanced bus tracking and terminal management system for BRT transport",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "app": "BRTLive",
        "version": "1.0.0",
        "description": "Real-time bus tracking and terminal management system",
        "endpoints": {
            "terminals": "/api/terminals",
            "buses": "/api/buses",
            "dashboard": "/api/dashboard"
        }
    }



@app.post("/api/terminals/register", tags=["Terminals"])
async def register_terminal(terminal: Terminal):
    result = bus_tracking_service.register_terminal(terminal)
    return result


@app.get("/api/terminals", tags=["Terminals"])
async def get_all_terminals():
    return {"terminals": list(bus_tracking_service.terminals.values())}


@app.get("/api/terminals/{terminal_id}", tags=["Terminals"])
async def get_terminal(terminal_id: str):
    
    if terminal_id not in bus_tracking_service.terminals:
        raise HTTPException(status_code=404, detail="Terminal not found")
    return bus_tracking_service.terminals[terminal_id]


@app.get("/api/terminals/{terminal_id}/dashboard", tags=["Terminals"])
async def get_terminal_dashboard(terminal_id: str):


    dashboard = bus_tracking_service.get_terminal_dashboard(terminal_id)
    if "error" in dashboard:
        raise HTTPException(status_code=404, detail=dashboard["error"])
    return dashboard



@app.post("/api/buses/register", tags=["Buses"])
async def register_bus(bus: Bus):
    result = bus_tracking_service.register_bus(bus)
    return result


@app.get("/api/buses", tags=["Buses"])
async def get_all_buses(
    status: Optional[str] = Query(None, description="Filter by status: available, in_transit, maintenance")
):
    buses = bus_tracking_service.get_all_buses()
    
    if status:
        buses = [bus for bus in buses if bus.status == status]
    
    return {"buses": buses, "count": len(buses)}


@app.get("/api/buses/{bus_id}", tags=["Buses"])
async def get_bus(bus_id: str):

    if bus_id not in bus_tracking_service.buses:
        raise HTTPException(status_code=404, detail="Bus not found")
    return bus_tracking_service.buses[bus_id]


@app.get("/api/buses/track/phone/{phone_number}", tags=["Buses"])
async def track_bus_by_phone(phone_number: str):

    bus = bus_tracking_service.get_bus_by_phone(phone_number)
    if not bus:
        raise HTTPException(status_code=404, detail="No bus found with this phone number")
    
    return {
        "bus": bus,
        "last_location": bus.last_location,
        "current_terminal": bus.current_terminal,
        "status": bus.status
    }


@app.post("/api/buses/{bus_id}/location", tags=["Buses"])
async def update_bus_location(bus_id: str, location: BusLocation):
    
    result = bus_tracking_service.update_bus_location(bus_id, location)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/api/buses/{bus_id}/location/history", tags=["Buses"])
async def get_location_history(
    bus_id: str,
    limit: int = Query(50, description="Number of recent locations to return")
):
    
    if bus_id not in bus_tracking_service.location_history:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    history = bus_tracking_service.location_history[bus_id]
    return {
        "bus_id": bus_id,
        "history": history[-limit:],
        "count": len(history)
    }


@app.patch("/api/buses/{bus_id}/status", tags=["Buses"])
async def update_bus_status(
    bus_id: str,
    status: str = Body(..., embed=True, description="Status: available, in_transit, maintenance")
):
    if bus_id not in bus_tracking_service.buses:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    valid_statuses = ["available", "in_transit", "maintenance"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    bus_tracking_service.buses[bus_id].status = status
    return {"message": "Status updated", "bus_id": bus_id, "new_status": status}



@app.get("/api/dashboard/overview", tags=["Dashboard"])
async def get_system_overview():
    dashboards = bus_tracking_service.get_all_terminals_dashboard()
    
    total_buses = len(bus_tracking_service.buses)
    available_buses = len([b for b in bus_tracking_service.buses.values() if b.status == "available"])
    in_transit = len([b for b in bus_tracking_service.buses.values() if b.status == "in_transit"])
    
    return {
        "timestamp": datetime.now(),
        "total_terminals": len(bus_tracking_service.terminals),
        "total_buses": total_buses,
        "available_buses": available_buses,
        "buses_in_transit": in_transit,
        "terminals": dashboards
    }


@app.get("/api/dashboard/wait-times", tags=["Dashboard"])
async def get_all_wait_times():
    wait_times = []
    for terminal_id, terminal in bus_tracking_service.terminals.items():
        estimate = bus_tracking_service._calc_wait_time(terminal_id)
        wait_times.append({
            "terminal_name": terminal.name,
            "terminal_id": terminal_id,
            "wait_estimate": estimate
        })
    
    return {"wait_times": wait_times, "timestamp": datetime.now()}


@app.get("/api/analytics/terminal/{terminal_id}", tags=["Analytics"])
async def get_terminal_analytics(terminal_id: str):
    if terminal_id not in bus_tracking_service.terminals:
        raise HTTPException(status_code=404, detail="Terminal not found")
    
    terminal = bus_tracking_service.terminals[terminal_id]
    dashboard = bus_tracking_service.get_terminal_dashboard(terminal_id)
    
    return {
        "terminal_id": terminal_id,
        "terminal_name": terminal.name,
        "current_buses": dashboard["buses_available"],
        "capacity": terminal.total_capacity,
        "utilization_percentage": dashboard["capacity_utilization"],
        "wait_estimate_minutes": dashboard["wait_estimate"].estimated_wait_minutes,
        "timestamp": datetime.now()
    }



@app.post("/api/dev/populate-sample-data", tags=["Development"], include_in_schema=False)
async def populate_sample_data():
    
    terminals = [
        Terminal(
            terminal_id="TRM001",
            name="CMS Terminal",
            latitude=6.4541,
            longitude=3.3947,
            total_capacity=20
        ),
        Terminal(
            terminal_id="TRM002",
            name="Mile 12 Terminal",
            latitude=6.5493,
            longitude=3.3844,
            total_capacity=15
        ),
        Terminal(
            terminal_id="TRM003",
            name="Ikorodu Terminal",
            latitude=6.6186,
            longitude=3.5064,
            total_capacity=18
        )
    ]
    
    for terminal in terminals:
        bus_tracking_service.register_terminal(terminal)
    
    
    buses = [
        Bus(bus_id="BUS001", driver_phone="+2348012345601", driver_name="John Adebayo", 
            plate_number="LAG-123AA", capacity=50, current_terminal="TRM001", status="available"),
        Bus(bus_id="BUS002", driver_phone="+2348012345602", driver_name="Mary Okafor", 
            plate_number="LAG-456BB", capacity=50, status="in_transit"),
        Bus(bus_id="BUS003", driver_phone="+2348012345603", driver_name="Ahmed Bello", 
            plate_number="LAG-789CC", capacity=50, current_terminal="TRM001", status="available"),
        Bus(bus_id="BUS004", driver_phone="+2348012345604", driver_name="Grace Nwosu", 
            plate_number="LAG-012DD", capacity=50, current_terminal="TRM002", status="available"),
    ]
    
    for bus in buses:
        bus_tracking_service.register_bus(bus)
    
    return {
        "message": "Sample data populated successfully",
        "terminals": len(terminals),
        "buses": len(buses)
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)