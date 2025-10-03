from pydantic import BaseModel,Field
from datetime import datetime,timezone

class TerminalBase(BaseModel):
 
  id:int
  name:str= Field(max_length=100)
  location: str
  longitude:float
  latitude:float
  created_at:datetime=datetime.now(timezone.utc)

  class Config:
    orm_mode=True

  
