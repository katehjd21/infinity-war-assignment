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


def test_toggle_coin_complete_server_error(mocker, logged_in_authenticated_user):
    client = logged_in_authenticated_user
    coin_id = "fake-coin-id"

    mocker.patch(
        "controllers.coin_controller.CoinController.toggle_coin_complete",
        return_value=None
    )

    response = client.post("/toggle_coin_complete", data={"coin_id": coin_id})
    assert response.status_code == 500
    assert response.data.decode() == "Server error"


def test_toggle_coin_complete_session_expired(mocker, logged_in_authenticated_user):
    client = logged_in_authenticated_user
    coin_id = "fake-coin-id"

    mocker.patch(
        "controllers.coin_controller.CoinController.toggle_coin_complete",
        side_effect=Exception("Session expired")
    )

    response = client.post("/toggle_coin_complete", data={"coin_id": coin_id}, follow_redirects=True)
    html = response.data.decode()

    with client.session_transaction() as session:
        assert session.get("username") is None
        assert session.get("role") is None

    assert "Your session has expired. Please log in again." in html
    assert "<h1>Login</h1>" in html
