from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import asyncio

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def hash_password(password: str) -> str:
    """Hash a password (async, CPU-intensive)"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, pwd_context.hash, password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash (async, CPU-intensive)"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        pwd_context.verify, 
        plain_password, 
        hashed_password
    )

def create_access_token(user_id: int) -> str:
    """Create JWT token (sync, fast operation)"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str) -> int:
    """Verify JWT token and return user_id (sync, fast operation)"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token payload")
        
        return int(user_id)
    
    except (JWTError, ValueError, KeyError) as e:
        raise ValueError("Invalid or expired token: " + str(e)) from e
