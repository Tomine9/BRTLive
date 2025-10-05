import re
from typing import Optional
from .constants import (NIGERIA_COUNTRY_CODE, PHONE_NUMBER_LENGTH,EMPLOYEE_ID_PREFIX,BUS_NUMBER_PREFIX)


def validate_employee_id(employee_id:str) -> bool:
    """
    Validate employee ID format
    Valid:  DRV001,DRV456326
    Invalid: drv,oo1,abd7659,DRV
    """
    if not employee_id:
        return False
    
    pattern = rf'^{EMPLOYEE_ID_PREFIX}\d{{3,5}}$'
    return bool (re.match(pattern,employee_id.upper()))

def validate_bus_number(bus_number:str) -> bool:
    """"
    Validate bus number format
    Valid: BRT-001, BRT-012
    Invalid: brt-001, BRT012,BRT
    """
    if not bus_number:
        return False
    pattern = rf'^{BUS_NUMBER_PREFIX}\d{{3}}$'
    return bool(re.match(pattern,bus_number.upper()))

def validate_nigerian_phone_code(phone:str) -> bool:
    """
    validate Nigerian phone number
    Valid: +2349017434715,+2347035130809
    Invalid: 08012345678, 2346789033463
    """
    if not phone:
        return False
    pattern = r'^\+234[678]\d{9}$'
    return bool(re.match(pattern,phone))

def validate_license_number(license_number:str) -> bool:
    """"
    Validate driver's license number
    Nigeria has no fixed format, so we keep it basic:
    - Must be alphanumeric
    -Length between 6-20 characters
    - can contain letters, numbers, hyphens
    """
    if not license_number:
        return False
    
    cleaned = license_number.replace(" ", "").replace("-", "")
    if len(cleaned)<6 or len(cleaned)>20:
        return False
    if not re.match(r'^[A-ZO-9]+$', cleaned.upper()):
        return False
    

def validate_coordinates(latitude:float, longitude:float)-> bool:
    """
    Validate GPS coordinates
    Lagos, Nigeria approximate bounds:
    Latitude: 6.4 to 6.7
    Longitude: 3.2 to 3.6
    """
    if not (-90 <= latitude <= 90):
        return False
    if not (-180 <= longitude <= 180):
        return False
    return True

def sanitize_phone_number(phone:str) -> str:
    """
    clean and standardize phone number
    Input: 09017434715, 8013246578, +2349017434715
    Output: +2348013246578
    """
    phone = phone.strip().replace(" ", "").replace("-","").replace("(", "").replace(")","")
    phone = phone.lstrip("0")
    
    if not phone.startswith("+"):
        if phone.startswith("234"):
            phone = "+" + phone
        else:
            phone = NIGERIA_COUNTRY_CODE + phone
    return phone

def sanitize_employee_id(employee_id: str) -> str:
    """employee_id to uppercase"""
    return employee_id.strip().upper()

def sanitize_bus_number(bus_number:str)->str:
    """ bus_number to uppercase"""
    return bus_number.strip().upper()