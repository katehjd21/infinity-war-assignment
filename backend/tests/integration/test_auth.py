from models import Coin

# TEST LOGIN
def test_login_success(client, create_admin_user):
    response = client.post("/login", json={
        "username": "admin",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Login successful"
    assert data["role"] == "admin"
    assert "session" in response.headers.get("Set-Cookie")


def test_login_fail_wrong_password(client):
    response = client.post("/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Invalid credentials" or "error" in data


def test_login_fail_nonexistent_user(client):
    response = client.post("/login", json={
        "username": "no_user",
        "password": "password"
    })
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data


# TEST LOGOUT
def test_logout_clears_session(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    response = client.post("/logout")
    data = response.get_json()
    assert response.status_code == 200
    assert data["message"] == "Logged out"


# TEST PROTECTED ROUTES
def test_protected_route_requires_login(client):
    response = client.post("/v3/coins", json={"name": "Test Coin"})
    assert response.status_code == 401


# TEST UNAUTHENTICATED USERS CAN SEE COINS/DUTIES AND COMPLETION
def test_unauthenticated_user_can_view_coins_and_completion(logged_in_admin, client, coin):
    logged_in_admin.post(f"/coins/{coin.id}/complete")

    logged_in_admin.post("/logout")

    response = client.get("/v3/coins")
    assert response.status_code == 200
    data = response.get_json()
    coin_data = next((c for c in data if c["id"] == str(coin.id)), None)
    assert coin_data is not None
    assert "completed" in data[0]



# TEST ADMIN CAN SEE HTTP REQUESTS
def test_admin_can_view_logs(logged_in_admin, create_admin_user):
    response = logged_in_admin.get("/admin/logs")
    assert response.status_code == 200
    data = response.get_json()
    if data:
        log = data[0]
        assert "method" in log
        assert "path" in log
        assert "user" in log
        assert "timestamp" in log


def test_non_admin_cannot_view_logs(client, create_authenticated_user):
    client.post("/login", json={
        "username": "authenticated_user",
        "password": "password"
    })

    response = client.get("/admin/logs")
    assert response.status_code == 403