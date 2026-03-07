import pytest
from flask import session

# LOGIN TESTS
def test_login_page_renders(client):
    response = client.get("/login")
    html = response.data.decode()
    assert response.status_code == 200
    assert "<h1>Login</h1>" in html

def test_login_invalid_credentials(mocker, client):
    mock_response = mocker.Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"error": "Invalid username or password"}
    mocker.patch("api_session.api_session.post", return_value=mock_response)

    response = client.post("/login", data={"username": "bad", "password": "bad"})
    html = response.data.decode()
    assert "Invalid username or password" in html

# LOGOUT TESTS
def test_logout_clears_session(logged_in_authenticated_user):
    client = logged_in_authenticated_user
    response = client.post("/logout", follow_redirects=True)
    html = response.data.decode()
    assert "Login" in html
    with client.session_transaction() as sess:
        assert sess.get("username") is None
        assert sess.get("role") is None


# ROLE ACCESS TESTS
@pytest.mark.parametrize(
    "url",
    [
        "/admin/coins",
        "/admin/coins/create",
        "/admin/duties",
        "/admin/logs"
    ]
)
def test_admin_routes_require_login(client, url):
    response = client.get(url, follow_redirects=True)
    html = response.data.decode()
    assert "You must be logged in to access this page." in html

def test_admin_routes_require_admin(client, logged_in_authenticated_user):
    client = logged_in_authenticated_user
    urls = [
        "/admin/coins",
        "/admin/coins/create",
        "/admin/duties",
        "/admin/logs"
    ]
    for url in urls:
        response = client.get(url, follow_redirects=True)
        html = response.data.decode()
        assert "You do not have permission to access this page." in html


# AUTHENTICATED USER COIN TOGGLE
def test_toggle_coin_complete_requires_login(client, mocked_coins):
    coin_id = mocked_coins[0].id
    response = client.post("/toggle_coin_complete", data={"coin_id": coin_id}, follow_redirects=True)
    html = response.data.decode()
    assert "You must be logged in to access this page." in html

def test_toggle_coin_complete_authenticated_user(mocker, logged_in_authenticated_user, mocked_coins):
    client = logged_in_authenticated_user
    coin_id = mocked_coins[0].id

    mocker.patch("controllers.coin_controller.CoinController.toggle_coin_complete", return_value=mocked_coins[0])

    response = client.post("/toggle_coin_complete", data={"coin_id": coin_id}, follow_redirects=True)
    html = response.data.decode()
    assert response.status_code == 200
    assert "Coins" in html or "<h1>Apprenticeship Coins</h1>" in html


# TEST ADMIN CREATE COIN/DUTY FLASH SUCCESS
def test_admin_create_coin_flash_success(mocker, logged_in_admin_user):
    client = logged_in_admin_user
    mocker.patch("controllers.coin_controller.CoinController.create_coin", return_value=("coin_obj", None))

    response = client.post(
        "/admin/coins/create",
        data={"name": "Coin A", "duty_codes": ""},
        follow_redirects=True
    )
    html = response.data.decode()
    
    assert "Coin created successfully." in html
    assert response.status_code == 200


def test_admin_create_duty_flash_success(mocker, logged_in_admin_user, mocked_coins):
    client = logged_in_admin_user

    mocker.patch(
        "controllers.duty_controller.DutyController.create_duty",
        return_value=("duty_obj", None)
    )

    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=mocked_coins
    )

    response = client.post(
        "/admin/duties/create",
        data={
            "code": "D100",
            "name": "New Duty",
            "description": "Duty Description",
            "coin_ids": [mocked_coins[0].id, mocked_coins[1].id],
            "ksb_codes": "K1,B1,S1"
        },
        follow_redirects=True
    )

    html = response.data.decode()
    
    assert "Duty created successfully." in html
    assert response.status_code == 200