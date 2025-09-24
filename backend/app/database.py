from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Generator
from contextlib import asynccontextmanager
import os

logger = logging.getLogger(__name__)

# =============================================================================
# 1. BASIC CONFIGURATION - Essential settings only
# =============================================================================

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

# Basic connection pool settings
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))

# =============================================================================
# 2. DATABASE BASE CLASS
# =============================================================================

Base = declarative_base()

# =============================================================================
# 3. ENGINE CREATION - Simple but robust
# =============================================================================

def create_database_engine():
    """Create database engine with essential configuration"""
    
    try:
        Engine = create_engine(
            DATABASE_URL,
            
            # Connection pool settings
            poolclass=QueuePool,
            pool_size=DB_POOL_SIZE,
            max_overflow=DB_MAX_OVERFLOW,
            pool_timeout=DB_POOL_TIMEOUT,
            pool_recycle=3600,  # Replace connections every hour
            pool_pre_ping=True,  # Test connections before use
            
            # Basic connection args
            connect_args={
                "connect_timeout": 10,
                "application_name": "BRTLive-Backend"
            },
            
            # Logging (only for development)
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )
        
        logger.info(f"✅ Database engine created successfully")
        return Engine
        
    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {e}")
        raise

# Create global engine
engine = create_database_engine()

# =============================================================================
# 4. SESSION SETUP - Simple session factory
# =============================================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =============================================================================
# 5. DATABASE DEPENDENCIES - For FastAPI and background tasks
# =============================================================================

def get_db() -> Generator[Session, None, None]:
    """Get database session for FastAPI endpoints"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@asynccontextmanager
async def get_async_db():
    """Async database session for background tasks (like ETA calculator)"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Async database error: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session() -> Session:
    """Get database session for simple operations"""
    return SessionLocal()

# =============================================================================
# 6. DATABASE UTILITIES - Essential functions
# =============================================================================

def test_connection() -> bool:
    """Test if database connection works"""
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()
        
        if result[0] == 1:
            logger.info("✅ Database connection test successful")
            return True
        else:
            logger.error("❌ Database connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

def create_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        raise

def get_connection_status() -> dict:
    """Get basic database connection status"""
    try:
        db = SessionLocal()
        
        # Test connection
        db.execute(text("SELECT 1"))
        
        # Get database version
        version_result = db.execute(text("SELECT version()")).fetchone()
        db_version = version_result[0] if version_result else "Unknown"
        
        # Get pool status
        pool = engine.pool
        pool_info = {
            "total_connections": pool.checkedout() + pool.checkedin(),
            "active_connections": pool.checkedout(),
            "pool_size": pool.size()
        }
        
        db.close()
        
        return {
            "status": "healthy",
            "version": db_version,
            "pool_info": pool_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get connection status: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# =============================================================================
# 7. INITIALIZATION FUNCTION - Setup everything
# =============================================================================

async def init_database():
    """Initialize database - call this on app startup"""
    logger.info("🚀 Initializing database...")
    
    # Test connection first
    if not test_connection():
        raise Exception("Database connection failed")
    
    # Create tables
    create_tables()
    
    logger.info("✅ Database initialization completed")
