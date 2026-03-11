import pytest
from unittest.mock import Mock

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


@pytest.mark.parametrize(
    "url",
    [
        "/admin/coins",
        "/admin/coins/create",
        "/admin/duties",
        "/admin/logs"
    ]
)
def test_admin_routes_require_admin(client, logged_in_authenticated_user, url):
    client = logged_in_authenticated_user
    response = client.get(url, follow_redirects=True)
    html = response.data.decode()
    assert "You do not have permission to access this page." in html


def test_admin_routes_session_expired(mocker, logged_in_admin_user):
    client = logged_in_admin_user

    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        side_effect=Exception("Session expired")
    )

    response = client.get("/admin/coins", follow_redirects=True)
    html = response.data.decode()

    with client.session_transaction() as session:
        assert session.get("username") is None
        assert session.get("role") is None

    assert "Your session has expired. Please log in again." in html
    assert "<h1>Login</h1>" in html