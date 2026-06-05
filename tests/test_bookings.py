def test_employee_can_create_booking(client, employee_token, room_with_slot):
    room, slot = room_with_slot

    response = client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "room_id": room.id,
            "slot_id": slot.id,
            "booking_date": "2026-06-05",
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
        "booking_date": "2026-06-05",
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