from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import asyncio
import uvicorn
import json
from datetime import datetime
import random

app = FastAPI(title="BRTLive", description="Advanced Transit Management System", version="1.0.0")

class BusLocation(BaseModel):
    bus_id: str
    latitude: float
    longitude: float
    speed: float
    direction: float
    timestamp: datetime

class Terminal(BaseModel):
    terminal_id: str
    name: str
    latitude: float
    longitude: float
    total_capacity: int

class BusAvaliability(BaseModel):
    terminal_id: str
    terminal_name: str
    buses_available: int
    total_capacity: int
    occupancy_rate: float
    expected_wait_time: int # in minutes
    next_arrivals: int

class Route(BaseModel):
    route_id: str
    name: str
    terminals: List[Terminal]
    frequency: int # buses per hour
    active: bool

class passengerCount(BaseModel):
    bus_id: str
    current_passengers: int
    max_capacity: int
    occupancy_rate: float

