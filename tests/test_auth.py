def test_login_success(client, employee_user):
    response = client.post(
        "/auth/token",
        data={
            "username": "employee",
            "password": "employee123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        "/auth/token",
        data={
            "username": "employee",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_get_me_success(client, employee_token):
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "employee"


def test_get_me_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401