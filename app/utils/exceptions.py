# Custom exceptions for BRTLive

class BRTLiveException(Exception):
    pass    #Base exception for BRTLive app.

class ValidationError(BRTLiveException):
    pass  # Data validation failed

class DriverNotVerifiedException(BRTLiveException):
    """ Driver hasn't been verified by admin"""
    def __int__(self):
        super().__init__("Driver acct pending admin verification")

class DriverAlreadyOnShiftException(BRTLiveException):
    """ Driver is already on an active shift"""
    def __init__(self):
        super().__init__("Driver already has an active shift")

class BusNotAvailableException(BRTLiveException):
    """ Bus is currently assigned to another driver"""
    def __init__(self, bus_number:str):
        super().__init__(f"Bus {bus_number} is currently in use")

class NoActiveShiftException(BRTLiveException):
    """Driver doesn't have an active shift"""
    def __init__(self):
        super().__init__("No active shift found for this driver")

class PhoneNumberMismatchException(BRTLiveException):
    """Phone number doesn't match driver record"""
    def __init__(self):
        super().__init__("Phone number doesn't match driver's records")

class InvalidCredentialsException(BRTLiveException):
    """Login credentials are invalid"""
    def __init__(self):
        super().__init__("Invalid username or password")

class GPSAccuracyException(BRTLiveException):
    """GPS accuracy is too poor"""
    def __init__(self, accuracy: float):
        super().__init__(f"GPS accuracy too poor: {accuracy}m (max 50m)")