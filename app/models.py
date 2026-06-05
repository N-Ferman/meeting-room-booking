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

class User(Base):
    __tablename__ = "users"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.employee,
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )


    bookings = relationship(
        "Booking",
        back_populates="user",
    )

class Room(Base):
    __tablename__ = "rooms"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )


    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )


    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )


    capacity: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )


    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )


    slots = relationship(
        "RoomSlot",
        back_populates="room",
    )


    bookings = relationship(
        "Booking",
        back_populates="room",
    )

class RoomSlot(Base):
    __tablename__ = "room_slots"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )


    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"),
        nullable=False,
    )


    start_time: Mapped[Time] = mapped_column(
        Time,
        nullable=False,
    )


    end_time: Mapped[Time] = mapped_column(
        Time,
        nullable=False,
    )


    room = relationship(
        "Room",
        back_populates="slots",
    )


    bookings = relationship(
        "Booking",
        back_populates="slot",
    )

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("room_slots.id"), nullable=False)
    booking_date = Column(Date, nullable=False)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    slot = relationship("RoomSlot", back_populates="bookings")

__table_args__ = (
    Index(
        "uq_active_booking_room_slot_date",
        "room_id",
        "slot_id",
        "booking_date",
        unique=True,
        postgresql_where=text("status = 'active'"),
    ),
)