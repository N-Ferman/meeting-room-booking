from datetime import time

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Room, RoomSlot, User, UserRole
from app.security import hash_password


def get_or_create_user(
    db: Session,
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
    db: Session,
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
    db: Session,
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


def seed_users(db: Session) -> None:
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


def seed_rooms_and_slots(db: Session) -> None:
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


def run_seed() -> None:
    db = SessionLocal()

    try:
        seed_users(db)
        seed_rooms_and_slots(db)
        print("Seed data created successfully")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
