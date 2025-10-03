# core/__init__.py
"""
Core functionality for BRT Live
- Security (auth, passwords)
- WebSocket (real-time updates)
- Cache (Redis)
- Logging
- Exceptions
"""

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

from app.core.websocket import manager, websocket_manager

from app.core.cache import (
    get_redis_client,
    cache_set,
    cache_get,
    cache_delete,
    cache_set_json,
    cache_get_json
)

from backend.app.core.Logging import setup_logging, get_logger

from app.core.exceptions import (
    BRTException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
    not_found,
    unauthorized,
    forbidden,
    bad_request
)

__all__ = [
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "verify_token",
    
    # WebSocket
    "manager",
    "websocket_manager",
    
    # Cache
    "get_redis_client",
    "cache_set",
    "cache_get",
    "cache_delete",
    "cache_set_json",
    "cache_get_json",
    
    # Logging
    "setup_logging",
    "get_logger",
    
    # Exceptions
    "BRTException",
    "NotFoundException",
    "UnauthorizedException",
    "ValidationException",
    "not_found",
    "unauthorized",
    "forbidden",
    "bad_request",
]