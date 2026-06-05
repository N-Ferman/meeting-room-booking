from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_admin
from app.models import Room, RoomSlot, User
from app.schemas import RoomCreate, RoomRead, RoomSlotCreate, RoomSlotRead


router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("", response_model=list[RoomRead])
def get_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Room).order_by(Room.id).all()

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