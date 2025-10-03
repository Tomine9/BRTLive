from pydantic import BaseModel
from datetime import datetime,timezone

class RouteBase(BaseModel):
    id:int
    name:str
    start_terminal_id:int
    end_terminal_id:int
    distance_km:float=0.0
    estimated_duration_minutes:int=45
    created_at:datetime=datetime.now(timezone.utc)

    class Config:
        orm_mode=True
