# xuserauth/models.py

from sqlalchemy import Column, String, Boolean, JSON, Integer, DateTime
from sqlalchemy.orm import declared_attr
from sqlalchemy.ext.declarative import as_declarative
from datetime import datetime


@as_declarative()
class Base:
    """
    Generic base class with automatic __tablename__.
    """
    id: int
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TimestampMixin:
    """
    Adds created_at and updated_at timestamp columns.
    """
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BaseUser(Base, TimestampMixin):
    """
    Abstract base user model with common fields and behaviors.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)

    roles = Column(JSON, default=["user"])
    social_ids = Column(JSON, default={})

    profile_picture = Column(String, nullable=True)  # e.g., URL to S3 or local path

    def __repr__(self):
        return f"<User(email='{self.email}', roles={self.roles})>"
