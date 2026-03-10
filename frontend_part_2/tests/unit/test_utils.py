import os
import json
from utils.helpers import load_fixture, is_valid_username, is_valid_password, login_api_session
from requests.models import Response
import requests

# LOAD FIXTURE
def test_load_fixture_returns_data():
    fixture_name = "test_utils.json"

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    fixtures_dir = os.path.join(project_root, "utils", "fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)

    fixture_path = os.path.join(fixtures_dir, fixture_name)

    sample_data = [{"id": "uuid-1", "name": "Test Coin"}]

    with open(fixture_path, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)

    try:
        result = load_fixture(fixture_name, folder="utils/fixtures")
        assert result == sample_data
    finally:
        os.remove(fixture_path)

    try:
        os.rmdir(fixtures_dir)
    except OSError:
        pass


# LOGIN API SESSION
def test_login_api_session_success(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"username": "testuser", "role": "admin"}

    mocker.patch("utils.helpers.api_session.post", return_value=mock_response)

    result = login_api_session("testuser", "password123")
    assert result == {"username": "testuser", "role": "admin"}


def test_login_api_session_failure_status(mocker):
    mock_response = mocker.Mock(spec=Response)
    mock_response.status_code = 401
    mock_response.json.return_value = {"error": "Invalid username or password"}

    mocker.patch("utils.helpers.api_session.post", return_value=mock_response)

    result = login_api_session("baduser", "badpass")
    assert result is None


def test_login_api_session_exception(mocker):
    mocker.patch(
        "utils.helpers.api_session.post",
        side_effect=requests.RequestException("Connection error")
    )

    result = login_api_session("testuser", "password123")

    assert result is None


# VALID USERNAME
def test_is_valid_username():
    assert is_valid_username("user123")
    assert is_valid_username("User_Name")
    assert is_valid_username("abc")

    assert not is_valid_username("ab")
    assert not is_valid_username("user@name")
    assert not is_valid_username("a" * 21)


# VALID PASSWORD
def test_is_valid_password():
    assert is_valid_password("123456")
    assert is_valid_password("password123")

    assert not is_valid_password("123")
    assert not is_valid_password("")