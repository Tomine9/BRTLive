from pydantic import BaseModel, Field
from datetime import datetime, timezone

class EtaBase(BaseModel):
    id:int
    bus_id:int  
    terminal_id:int
    estimated_arrival_time: datetime
    estimated_minutes_away:int
    confidence_level:float=0.8
    prediction_method: str= Field(max_length=50, default= "real_time")
    calculated_from_phone_location:bool=True
    last_phone_update_used:datetime|None
    calculated_at: datetime= Field(default=datetime.now(timezone.utc))
    last_updated:datetime= Field(default=datetime.now(timezone.utc),onupdate=datetime.now(timezone.utc))
    is_active:bool=True

    class Config:
        orm_mode=True

class ShowEta(BaseModel):
    bus_id:int
    estimated_arrival_time:datetime
    estimated_minutes_away:int

