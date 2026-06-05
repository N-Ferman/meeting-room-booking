from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import Booking, BookingStatus, Room, RoomSlot, User
from app.schemas import BookingCreate, BookingRead


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.id == booking_data.room_id).first()

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    slot = db.query(RoomSlot).filter(RoomSlot.id == booking_data.slot_id).first()

    if slot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found",
        )

    if slot.room_id != booking_data.room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot does not belong to this room",
        )

    if booking_data.booking_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking date cannot be in the past",
        )

    existing_booking = (
        db.query(Booking)
        .filter(
            Booking.room_id == booking_data.room_id,
            Booking.slot_id == booking_data.slot_id,
            Booking.booking_date == booking_data.booking_date,
            Booking.status == BookingStatus.active,
        )
        .first()
    )

    if existing_booking is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This room slot is already booked",
        )

    booking = Booking(
        user_id=current_user.id,
        room_id=booking_data.room_id,
        slot_id=booking_data.slot_id,
        booking_date=booking_data.booking_date,
        status=BookingStatus.active,
    )

    db.add(booking)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This room slot is already booked",
        )

    db.refresh(booking)

    return booking