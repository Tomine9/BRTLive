from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Custom base exceptions
class BRTException(Exception):
    """Base exception for BRT Live"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(BRTException):
    """Resource not found"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)

class UnauthorizedException(BRTException):
    """Unauthorized access"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)

class ForbiddenException(BRTException):
    """Access forbidden"""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, 403)

class ValidationException(BRTException):
    """Validation error"""
    def __init__(self, message: str = "Invalid request"):
        super().__init__(message, 400)

class ConflictException(BRTException):
    """Resource conflict"""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, 409)

class DatabaseException(BRTException):
    """Database operation failed"""
    def __init__(self, message: str = "Database error"):
        super().__init__(message, 500)

# Async exception handlers
async def brt_exception_handler(exc: BRTException) -> JSONResponse:
    """Handle custom BRT exceptions"""
    logger.error(f"BRT Exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

async def validation_exception_handler(exc: ValidationException) -> JSONResponse:
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

async def database_exception_handler(exc: DatabaseException) -> JSONResponse:
    """Handle database errors"""
    logger.error(f"Database error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": "Database operation failed"}
    )

# Quick raise functions
def not_found(detail: str = "Resource not found"):
    """Raise 404 error"""
    raise NotFoundException(detail)

def unauthorized(detail: str = "Authentication required"):
    """Raise 401 error"""
    raise UnauthorizedException(detail)

def forbidden(detail: str = "Access forbidden"):
    """Raise 403 error"""
    raise ForbiddenException(detail)

def bad_request(detail: str = "Invalid request"):
    """Raise 400 error"""
    raise ValidationException(detail)

def conflict(detail: str = "Resource conflict"):
    """Raise 409 error"""
    raise ConflictException(detail)

def server_error(detail: str = "Internal server error"):
    """Raise 500 error"""
    raise BRTException(detail, 500)
