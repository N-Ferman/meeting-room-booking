from datetime import time, date, datetime
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class UserRead(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class RoomCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    capacity: int | None = None


class RoomRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    capacity: int | None = None

    class Config:
        from_attributes = True

class RoomSlotCreate(BaseModel):
    start_time: time
    end_time: time


class RoomSlotRead(BaseModel):
    id: int
    room_id: int
    start_time: time
    end_time: time

    class Config:
        from_attributes = True

class AvailabilitySlotRead(BaseModel):
    slot_id: int
    start_time: time
    end_time: time
    is_available: bool
    booking_id: int | None = None


class RoomAvailabilityRead(BaseModel):
    room_id: int
    room_name: str
    slots: list[AvailabilitySlotRead]

class BookingCreate(BaseModel):
    room_id: int
    slot_id: int
    booking_date: date


class BookingRead(BaseModel):
    id: int
    user_id: int
    room_id: int
    slot_id: int
    booking_date: date
    status: str
    created_at: datetime
    cancelled_at: datetime | None = None

    class Config:
        from_attributes = True