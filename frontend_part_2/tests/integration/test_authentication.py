import pytest


# LOGOUT
def test_logout_clears_session(mock_api_session_post, logged_in_authenticated_user):
    mock_api_session_post("app", {"message": "Logged out"})

    client = logged_in_authenticated_user
    response = client.post("/logout", follow_redirects=True)
    html = response.data.decode()

    assert "Login" in html
    with client.session_transaction() as sess:
        assert sess.get("username") is None
        assert sess.get("role") is None


# ROLE ACCESS
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
