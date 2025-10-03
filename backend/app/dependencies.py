from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import redis.asyncio as redis
from datetime import datetime

from app.database import async_session
from app.core.security import verify_token
from app.core.cache import get_redis_client
from backend.app.core.Logging import get_logger
from app.models.user import User

# Security
security = HTTPBearer()

async def get_db() -> AsyncSession:
    """Get async database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_active_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        user_id = verify_token(token)
        
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if user.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account disabled"
            )
        
        return user
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        ) from e

async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require admin role"""
    if current_user.is_admin is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def require_driver(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require driver role"""
    if current_user.role not in ["driver", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver access required"
        )
    return current_user

async def get_cache() -> redis.Redis:
    """Get async Redis cache client"""
    return await get_redis_client()

def get_app_logger():
    """Get application logger"""
    return get_logger("brt-live")

# Optional token (for public endpoints that can show more data if user is logged in)
async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """Get user if token provided, otherwise None"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_id = verify_token(token)
        
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()
    except (HTTPException, ValueError):
        return None

# Rate limiting dependency
def rate_limit_key(request) -> str:
    """Generate rate limit key from request"""
    client_ip = request.client.host
    return f"rate_limit:{client_ip}:{datetime.now().strftime('%Y-%m-%d:%H:%M')}"