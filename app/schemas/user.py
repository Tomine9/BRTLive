from pydantic import BaseModel,Field
from datetime import datetime,timezone

class UserBase(BaseModel):
    id: int
    is_active:bool=True
    last_enter:datetime | None=None
    created_at:datetime= Field(default=datetime.now(timezone.utc))
    
    class Config:
        orm_mode=True
   