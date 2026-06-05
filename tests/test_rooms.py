def test_employee_can_get_rooms(client, employee_token, room_with_slot):
    response = client.get(
        "/rooms",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_employee_cannot_create_room(client, employee_token):
    response = client.post(
        "/rooms",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "name": "Room A",
            "description": "Small meeting room",
            "capacity": 6,
        },
    )

    assert response.status_code == 403


def test_admin_can_create_room(client, admin_token):
    response = client.post(
        "/rooms",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Room A",
            "description": "Small meeting room",
            "capacity": 6,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Room A"
    assert data["capacity"] == 6


def test_admin_can_create_room_slot(client, admin_token, room_with_slot):
    room, _ = room_with_slot

    response = client.post(
        f"/rooms/{room.id}/slots",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "start_time": "11:00:00",
            "end_time": "13:00:00",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["room_id"] == room.id
    assert data["start_time"] == "11:00:00"
    assert data["end_time"] == "13:00:00"


def test_cannot_create_invalid_slot(client, admin_token, room_with_slot):
    room, _ = room_with_slot

    response = client.post(
        f"/rooms/{room.id}/slots",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "start_time": "13:00:00",
            "end_time": "11:00:00",
        },
    )

    assert response.status_code == 400