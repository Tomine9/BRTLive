import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship


from app.database import Base

class UserRole(str, enum.Enum):
    """User role types"""
    ADMIN = "admin"
    DRIVER = "driver"
    VIEWER = "viewer"

class User(Base):
    """
    User model for authentication and authorization.
    Handles admins, drivers and viewers.
    """
    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)
    
    # Security
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    verification_token = Column(String(255), nullable=True)
    
    # Relationships
    # If user is a driver, link to driver profile
    driver = relationship("Driver", back_populates="user", uselist=False)
    
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_driver(self) -> bool:
        """Check if user is a driver"""
        return self.role == UserRole.DRIVER
    
    def can_manage_buses(self) -> bool:
        """Check if user can manage buses"""
        return self.role in [UserRole.ADMIN]
    
    def can_view_dashboard(self) -> bool:
        """Check if user can access dashboard"""
        return self.role in [UserRole.ADMIN, UserRole.VIEWER]
    
    def can_drive(self) -> bool:
        """Check if user can drive buses"""
        return self.role in [UserRole.DRIVER, UserRole.ADMIN]
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    def to_dict(self):
        """Convert to dictionary (for JSON responses)"""
        return {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
# Create new user
# user = User(
#     email="john@example.com",
#     password_hash=hash_password("secret123"),
#     first_name="John",
#     last_name="Doe",
#     role=UserRole.DRIVER
# )

# # Check permissions
# if user.can_drive():
#     assign_bus_to_user(user)

# # Get full info
# user_data = user.to_dict()