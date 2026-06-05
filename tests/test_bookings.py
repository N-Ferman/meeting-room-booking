BOOKING_DATE = "2030-01-01"


def test_employee_can_create_booking(client, employee_token, room_with_slot):
    room, slot = room_with_slot

    response = client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "room_id": room.id,
            "slot_id": slot.id,
            "booking_date": BOOKING_DATE,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["room_id"] == room.id
    assert data["slot_id"] == slot.id
    assert data["status"] == "active"


def test_cannot_create_duplicate_booking(client, employee_token, room_with_slot):
    room, slot = room_with_slot

    payload = {
        "room_id": room.id,
        "slot_id": slot.id,
        "booking_date": BOOKING_DATE,
    }

    first_response = client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {employee_token}"},
        json=payload,
    )

    second_response = client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {employee_token}"},
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_employee_can_get_own_bookings(client, employee_token, room_with_slot):
    room, slot = room_with_slot

    client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "room_id": room.id,
            "slot_id": slot.id,
            "booking_date": BOOKING_DATE,
        },
    )

    response = client.get(
        "/bookings/my",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_employee_can_cancel_own_booking(client, employee_token, room_with_slot):
    room, slot = room_with_slot

    create_response = client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "room_id": room.id,
            "slot_id": slot.id,
            "booking_date": BOOKING_DATE,
        },
    )

    booking_id = create_response.json()["id"]

    cancel_response = client.delete(
        f"/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"


def test_employee_cannot_cancel_other_user_booking(
    client,
    employee_token,
    second_employee_token,
    room_with_slot,
):
    room, slot = room_with_slot

    create_response = client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "room_id": room.id,
            "slot_id": slot.id,
            "booking_date": BOOKING_DATE,
        },
    )

    booking_id = create_response.json()["id"]

    cancel_response = client.delete(
        f"/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {second_employee_token}"},
    )

    assert cancel_response.status_code == 403


def test_admin_can_cancel_any_booking(
    client,
    employee_token,
    admin_token,
    room_with_slot,
):
    room, slot = room_with_slot

    create_response = client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "room_id": room.id,
            "slot_id": slot.id,
            "booking_date": BOOKING_DATE,
        },
    )

    booking_id = create_response.json()["id"]

    cancel_response = client.delete(
        f"/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"


def test_availability_shows_booked_slot(client, employee_token, room_with_slot):
    room, slot = room_with_slot

    create_response = client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "room_id": room.id,
            "slot_id": slot.id,
            "booking_date": BOOKING_DATE,
        },
    )

    booking_id = create_response.json()["id"]

    availability_response = client.get(
        f"/rooms/availability?date={BOOKING_DATE}",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert availability_response.status_code == 200

    data = availability_response.json()

    assert data[0]["room_id"] == room.id
    assert data[0]["slots"][0]["slot_id"] == slot.id
    assert data[0]["slots"][0]["is_available"] is False
    assert data[0]["slots"][0]["booking_id"] == booking_id