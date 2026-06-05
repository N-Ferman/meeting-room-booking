from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import time
from app.dependencies import get_current_user, get_db, SessionLocal
from app.models import Room, RoomSlot, User, UserRole
from app.schemas import Token, UserRead
from app.security import create_access_token, verify_password, hash_password


router = APIRouter(prefix="/auth", tags=["Auth"])


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user

def get_or_create_user(
    db,
    username: str,
    password: str,
    role: UserRole,
) -> User:
    user = db.query(User).filter(User.username == username).first()

    if user is not None:
        return user

    user = User(
        username=username,
        hashed_password=hash_password(password),
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_or_create_room(
    db,
    name: str,
    description: str,
    capacity: int,
) -> Room:
    room = db.query(Room).filter(Room.name == name).first()

    if room is not None:
        return room

    room = Room(
        name=name,
        description=description,
        capacity=capacity,
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return room


def get_or_create_slot(
    db,
    room_id: int,
    start_time: time,
    end_time: time,
) -> RoomSlot:
    slot = (
        db.query(RoomSlot)
        .filter(
            RoomSlot.room_id == room_id,
            RoomSlot.start_time == start_time,
            RoomSlot.end_time == end_time,
        )
        .first()
    )

    if slot is not None:
        return slot

    slot = RoomSlot(
        room_id=room_id,
        start_time=start_time,
        end_time=end_time,
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)

    return slot


def seed_users(db):
    get_or_create_user(
        db=db,
        username="admin",
        password="admin123",
        role=UserRole.admin,
    )

    get_or_create_user(
        db=db,
        username="employee",
        password="employee123",
        role=UserRole.employee,
    )

    get_or_create_user(
        db=db,
        username="employee2",
        password="employee123",
        role=UserRole.employee,
    )


def seed_rooms_and_slots(db):
    rooms = [
        {
            "name": "Room A",
            "description": "Small meeting room",
            "capacity": 6,
        },
        {
            "name": "Room B",
            "description": "Medium meeting room",
            "capacity": 10,
        },
        {
            "name": "Room C",
            "description": "Large conference room",
            "capacity": 20,
        },
    ]

    slots = [
        (time(9, 0), time(11, 0)),
        (time(11, 0), time(13, 0)),
        (time(13, 0), time(16, 0)),
        (time(16, 0), time(18, 0)),
    ]

    for room_data in rooms:
        room = get_or_create_room(
            db=db,
            name=room_data["name"],
            description=room_data["description"],
            capacity=room_data["capacity"],
        )

        for start_time, end_time in slots:
            get_or_create_slot(
                db=db,
                room_id=room.id,
                start_time=start_time,
                end_time=end_time,
            )


def run_seed():
    db = SessionLocal()

    try:
        seed_users(db)
        seed_rooms_and_slots(db)
        print("Seed data created successfully")

    finally:
        db.close()


if __name__ == "__main__":
    run_seed()