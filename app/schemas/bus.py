from pydantic import BaseModel,Field
from datetime import datetime
from models.Bus import BusStatus

class BusBase(BaseModel):
    id:int
    plate_number:str
    capacity:int
    status:BusStatus
    current_passenger_count:int
    is_available:bool
    is_active:bool
    created_at:datetime

    class Config:
        orm_mode = True

class BusCreate(BaseModel):
    plate_number:str
    capacity:int
    route_id:int | None= None
    bus_status:BusStatus= Field(default=BusStatus.OUT_OF_SERVICE)


