from pydantic import BaseModel
from datetime import datetime

class BusAssignmentBase(BaseModel):
    id:int
    bus_id:int
    driver_id:int
    start_shift:datetime
    end_shift:datetime|None
    planned_shift_duration: int=8
    tracking_started_at:datetime|None
    tracking_ended_at:datetime|None
    assignment_status:str="assigned"
    created_at:datetime

    class Config:
        orm_mode=True

class BusAssignmentCreate(BaseModel):
    bus_id:int
    driver_id:int
    start_shift:datetime
    end_shift:datetime|None = None


