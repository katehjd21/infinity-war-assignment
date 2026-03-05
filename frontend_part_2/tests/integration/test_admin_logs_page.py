from unittest.mock import Mock
import requests
import pytest

@pytest.fixture
def mock_admin_logs(mocker):
    mock_logs = [
        {"method": "GET", "path": "/login", "user": "user1", "timestamp": "2026-03-05T10:00:00Z"},
        {"method": "POST", "path": "/coin/1", "user": "user2", "timestamp": "2026-03-05T10:05:00Z"},
    ]
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_logs
    mocker.patch("requests.get", return_value=mock_response)
    return mock_logs


def test_admin_logs_page_as_admin(mocker, logged_in_admin_user, mock_admin_logs):
    response = logged_in_admin_user.get("/admin/logs")
    html = response.data.decode()

    assert response.status_code == 200
    assert "<h1>Last 100 HTTP Requests</h1>" in html
    for log in mock_admin_logs:
        assert log["method"] in html
        assert log["path"] in html
        assert log["user"] in html
        assert log["timestamp"] in html


def test_admin_logs_page_unauthorized(logged_in_authenticated_user):
    response = logged_in_authenticated_user.get("/admin/logs")
    assert response.status_code == 401
    assert "Unauthorized" in response.data.decode()


def test_admin_logs_page_server_error(mocker, logged_in_admin_user):
    mocker.patch("requests.get", side_effect=requests.RequestException("Server error"))

    response = logged_in_admin_user.get("/admin/logs")
    html = response.data.decode()

    assert response.status_code == 200
    assert "<h1>Last 100 HTTP Requests</h1>" in html
    assert "<td>" not in html
    assert "<th>Method</th>" in html
    assert "<th>Path</th>" in html
    assert "<th>User</th>" in html
    assert "<th>Timestamp</th>" in html