from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_admin
from app.models import Booking, BookingStatus, Room, RoomSlot, User
from app.schemas import (
    RoomAvailabilityRead,
    RoomCreate,
    RoomRead,
    RoomSlotCreate,
    RoomSlotRead,
)


router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("", response_model=list[RoomRead])
def get_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Room).order_by(Room.id).all()


@router.get("/availability", response_model=list[RoomAvailabilityRead])
def get_rooms_availability(
    requested_date: date = Query(alias="date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rooms = db.query(Room).order_by(Room.id).all()

    active_bookings = (
        db.query(Booking)
        .filter(
            Booking.booking_date == requested_date,
            Booking.status == BookingStatus.active,
        )
        .all()
    )

    bookings_by_room_and_slot = {
        (booking.room_id, booking.slot_id): booking
        for booking in active_bookings
    }

    result = []

    for room in rooms:
        room_slots = sorted(room.slots, key=lambda slot: slot.start_time)

        slots = []

        for slot in room_slots:
            booking = bookings_by_room_and_slot.get((room.id, slot.id))

            slots.append(
                {
                    "slot_id": slot.id,
                    "start_time": slot.start_time,
                    "end_time": slot.end_time,
                    "is_available": booking is None,
                    "booking_id": booking.id if booking else None,
                }
            )

        result.append(
            {
                "room_id": room.id,
                "room_name": room.name,
                "slots": slots,
            }
        )

    return result


@router.get("/{room_id}", response_model=RoomRead)
def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.id == room_id).first()

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return room


@router.post("", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing_room = db.query(Room).filter(Room.name == room_data.name).first()

    if existing_room is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room with this name already exists",
        )

    room = Room(
        name=room_data.name,
        description=room_data.description,
        capacity=room_data.capacity,
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return room


@router.post(
    "/{room_id}/slots",
    response_model=RoomSlotRead,
    status_code=status.HTTP_201_CREATED,
)
def create_room_slot(
    room_id: int,
    slot_data: RoomSlotCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.id == room_id).first()

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    if slot_data.start_time >= slot_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot start time must be earlier than end time",
        )

    existing_slot = (
        db.query(RoomSlot)
        .filter(
            RoomSlot.room_id == room_id,
            RoomSlot.start_time == slot_data.start_time,
            RoomSlot.end_time == slot_data.end_time,
        )
        .first()
    )

    if existing_slot is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This slot already exists for this room",
        )

    slot = RoomSlot(
        room_id=room_id,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time,
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)

    return slot