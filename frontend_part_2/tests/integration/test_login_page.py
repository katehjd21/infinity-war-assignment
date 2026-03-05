import pytest
from unittest.mock import Mock
from app import api_session
import requests

@pytest.fixture
def valid_login_data():
    return {"username": "valid_user", "password": "valid_password"}

@pytest.fixture
def invalid_login_data():
    return {"username": "invalid_user", "password": "invalid_password"}

def test_login_page_get(client):
    response = client.get("/login")
    html = response.data.decode()
    assert response.status_code == 200
    assert "<h1>Login</h1>" in html

def test_login_page_post_valid_credentials(mocker, client, valid_login_data):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"role": "authenticated"}
    mocker.patch.object(api_session, "post", return_value=mock_response)

    response = client.post("/login", data=valid_login_data, follow_redirects=True)

    html = response.data.decode()
    assert response.status_code == 200
    assert "<h1>Apprenticeship Coins</h1>" in html
    with client.session_transaction() as session:
        assert session["username"] == "valid_user"
        assert session["role"] == "authenticated"

def test_login_page_post_invalid_credentials(mocker, client, invalid_login_data):
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"error": "Invalid credentials"}
    mocker.patch.object(api_session, "post", return_value=mock_response)

    response = client.post("/login", data=invalid_login_data)
    html = response.data.decode()
    assert response.status_code == 200
    assert "Invalid credentials" in html

def test_login_page_post_server_error(mocker, client, valid_login_data):
    mocker.patch.object(api_session, "post", side_effect=requests.RequestException("Server error"))

    response = client.post("/login", data=valid_login_data)
    html = response.data.decode()
    assert response.status_code == 200
    assert "Server error. Try again later." in html