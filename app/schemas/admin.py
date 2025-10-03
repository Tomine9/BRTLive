from pydantic import BaseModel, Field
from datetime import datetime

class AdminBase(BaseModel):
    id:int
    username: str
    first_name:str
    last_name:str
    email:str
    is_super_admin:bool
    is_active:bool
    created_at:datetime

    class Config:
        orm_mode = True

class AdminCreate(BaseModel):
    first_name:str
    last_name:str
    username:str
    password:str= Field(min_length=6)
    is_super_admin:bool= False

class AdminLogin(BaseModel):
    username: str
    password:str
    #this