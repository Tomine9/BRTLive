from pydantic import BaseModel,Field
from datetime import datetime,timezone

class TrackingBase(BaseModel):
    id:int
    bus_id:int
    route_id:int
    driver_id:int
    driver_phone_number:str=Field(max_length=20)
    longitude:float
    Latitude:float
    accuracy_meters:float=10.0
    speed_km:float
    heading:float
    altitude:float
    phone_battery_level:int | None=None
    is_charging: bool=False
    network_type:str | None=None
    signal_strength:str|None=None
    last_phone_ping:datetime|None=None
    last_updated:datetime= Field(datetime.now(timezone.utc), onupdate= datetime.now(timezone.utc))

    class Config:
        orm_mode=True
