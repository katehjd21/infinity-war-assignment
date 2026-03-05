import pytest
from unittest.mock import Mock
from models.duty import Duty
import requests


@pytest.fixture
def mock_api_session_get(mocker):
    def _mock(response_data):
        mock_response = Mock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mocker.patch("models.duty.api_session.get", return_value=mock_response)
    return _mock


def test_fetch_single_duty_with_coins_from_backend(mock_api_session_get, mocked_duty_response):
    mock_api_session_get(mocked_duty_response)

    duty = Duty.fetch_duty_from_backend(mocked_duty_response["code"])
    assert duty.code == "D1"
    assert duty.name == "Duty 1"
    assert duty.coins == mocked_duty_response["coins"]


def test_fetch_single_duty_with_missing_coins_from_backend(mock_api_session_get):
    response_data = {"code": "D1", "name": "Duty 1", "description": "Duty 1 Description"}

    mock_api_session_get(response_data)

    duty = Duty.fetch_duty_from_backend(response_data["code"])
    
    assert duty.coins == []


def test_fetch_duty_raises_request_exception(mocker):
    mocker.patch("models.duty.api_session.get", side_effect=requests.RequestException("Network error"))
    duty = Duty.fetch_duty_from_backend("D99")
    assert duty is None