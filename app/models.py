import enum

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class UserRole(str, enum.Enum):
    employee = "employee"
    admin = "admin"

class BookingStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"