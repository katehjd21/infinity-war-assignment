import requests


def test_login_page_renders(client):
    response = client.get("/login")
    html = response.data.decode()
    assert response.status_code == 200
    assert "<h1>Login</h1>" in html


def test_login_page_post_valid_credentials(mocker, client, valid_login_data, mocked_coins):
    mocker.patch("app.login_api_session", return_value={"role": "authenticated"})
    mocker.patch("app.CoinController.fetch_all_coins", return_value=mocked_coins)

    response = client.post("/login?testing=1", data=valid_login_data, follow_redirects=True)
    html = response.data.decode()

    assert response.status_code == 200
    assert "<h1>Apprenticeship Coins</h1>" in html

    with client.session_transaction() as session:
        assert session["username"] == valid_login_data["username"]
        assert session["role"] == "authenticated"


def test_login_page_post_invalid_credentials(mocker, client, invalid_login_data):
    mocker.patch("utils.helpers.login_api_session", return_value=None)

    response = client.post("/login", data=invalid_login_data)
    html = response.data.decode()

    assert response.status_code == 200
    assert "Invalid credentials" in html


def test_login_page_post_server_error(mocker, client, valid_login_data):
    mocker.patch("app.login_api_session", side_effect=requests.RequestException("Server error"))

    response = client.post("/login", data=valid_login_data)
    html = response.data.decode()

    assert response.status_code == 200
    assert "Server error. Try again later." in html