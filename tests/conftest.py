from datetime import time

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Booking, Room, RoomSlot, User, UserRole
from app.security import hash_password


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    db = SessionLocal()

    try:
        db.query(Booking).delete()
        db.query(RoomSlot).delete()
        db.query(Room).delete()
        db.query(User).delete()
        db.commit()

        yield

        db.query(Booking).delete()
        db.query(RoomSlot).delete()
        db.query(Room).delete()
        db.query(User).delete()
        db.commit()

    finally:
        db.close()


@pytest.fixture
def db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def create_test_user(
    db,
    username: str,
    password: str,
    role: UserRole,
):
    user = User(
        username=username,
        hashed_password=hash_password(password),
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def admin_user(db):
    return create_test_user(
        db=db,
        username="admin",
        password="admin123",
        role=UserRole.admin,
    )


@pytest.fixture
def employee_user(db):
    return create_test_user(
        db=db,
        username="employee",
        password="employee123",
        role=UserRole.employee,
    )


@pytest.fixture
def second_employee_user(db):
    return create_test_user(
        db=db,
        username="employee2",
        password="employee123",
        role=UserRole.employee,
    )


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "admin123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def employee_token(client, employee_user):
    response = client.post(
        "/auth/token",
        data={
            "username": "employee",
            "password": "employee123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def second_employee_token(client, second_employee_user):
    response = client.post(
        "/auth/token",
        data={
            "username": "employee2",
            "password": "employee123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def room_with_slot(db):
    room = Room(
        name="Room A",
        description="Small meeting room",
        capacity=6,
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    slot = RoomSlot(
        room_id=room.id,
        start_time=time(9, 0),
        end_time=time(11, 0),
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)

    return room, slot