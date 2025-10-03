from pydantic import BaseModel, Field
from datetime import datetime, timezone

class DriverBase(BaseModel):
    id: int
    employees_id: str
    first_name: str
    last_name: str
    phone_number:str
    license_number:str
    is_active:bool=True
    created_at:datetime=Field(default=datetime.now(timezone.utc))

    class Config:
        orm_mode=True

class DriverRegister(BaseModel):
    first_name:str
    last_name:str
    employee_id:str
    license_number:str
    phone_number=str= Field(min_length=11, max_length=15)
    password: str= Field(min_length=8)

class DriverLogin(BaseModel):
    employee_id:str
    password:str

class DriverStartShift(BaseModel):
    bus_id:int
    employee_id:str
    phone_number: str=Field(min_length=11,max_length=15)
