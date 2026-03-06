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


@pytest.fixture
def mock_api_session_post(mocker):
    def _mock(response_data):
        mock_response = Mock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mocker.patch("models.duty.api_session.post", return_value=mock_response)
    return _mock


@pytest.fixture
def mock_api_session_patch(mocker):
    def _mock(response_data):
        mock_response = Mock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mocker.patch("models.duty.api_session.patch", return_value=mock_response)
    return _mock


@pytest.fixture
def mock_api_session_delete(mocker):
    def _mock(return_value=True):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mocker.patch("models.duty.api_session.delete", return_value=mock_response)
        return mock_response
    return _mock


# FETCH DUTY
def test_fetch_duty_success(mock_api_session_get):
    response_data = {
        "id": "1",
        "code": "D1",
        "name": "Duty 1",
        "description": "Duty 1 Description",
        "coins": [{"id": "C1", "name": "Automate"}],
        "ksbs": ["K1", "S1"]
    }
    mock_api_session_get(response_data)

    duty = Duty.fetch_duty_from_backend("D1")
    assert duty.code == "D1"
    assert duty.name == "Duty 1"
    assert duty.coins == response_data["coins"]
    assert duty.ksbs == response_data["ksbs"]


def test_fetch_duty_defaults_for_missing_fields(mock_api_session_get):
    response_data = {"code": "D2", "name": "Duty 2", "description": "Duty 2 Description"}
    mock_api_session_get(response_data)

    duty = Duty.fetch_duty_from_backend("D2")
    assert duty.code == "D2"
    assert duty.coins == []
    assert duty.ksbs == []


def test_fetch_duty_returns_none_on_error(mocker):
    mocker.patch("models.duty.api_session.get", side_effect=requests.RequestException("Network error"))
    duty = Duty.fetch_duty_from_backend("D99")
    assert duty is None


# CREATE DUTY
def test_create_duty_success(mock_api_session_post):
    response_data = {
        "id": "2",
        "code": "D10",
        "name": "Duty 10",
        "description": "Duty 10 Description",
        "coins": [{"id": "C1", "name": "Automate"}],
        "ksbs": ["K1", "S1"]
    }
    mock_api_session_post(response_data)

    duty = Duty.create_duty(
        "D10",
        "Duty 10",
        "Duty 10 Description",
        coin_ids=["C1"],
        ksb_codes=["K1", "S1"]
    )

    assert duty.id == "2"
    assert duty.code == "D10"
    assert duty.coins == response_data["coins"]
    assert duty.ksbs == ["K1", "S1"]


def test_create_duty_returns_none_on_error(mocker):
    mocker.patch("models.duty.api_session.post", side_effect=requests.RequestException("Error"))
    duty = Duty.create_duty("D1", "Fail Duty", "Fail Description")
    assert duty is None


# UPDATE DUTY
def test_update_duty_success(mock_api_session_patch):
    response_data = {
        "id": "3",
        "code": "D3",
        "name": "Updated Duty",
        "description": "Updated Description",
        "coins": [{"id": "C2", "name": "Houston"}],
        "ksbs": ["K2", "S2"]
    }
    mock_api_session_patch(response_data)

    duty = Duty.update_duty(
        code="D3",
        name="Updated Duty",
        description="Updated Description",
        coin_ids=["C2"],
        ksb_codes=["K2", "S2"]
    )

    assert duty.name == "Updated Duty"
    assert duty.description == "Updated Description"
    assert duty.coins == response_data["coins"]
    assert duty.ksbs == ["K2", "S2"]


def test_update_duty_partial_update(mock_api_session_patch):
    response_data = {"id": "4", "code": "D4", "name": "Name Only", "description": "", "coins": [], "ksbs": []}
    mock_api_session_patch(response_data)

    duty = Duty.update_duty(code="D4", name="Name Only")
    assert duty.name == "Name Only"
    assert duty.description == ""
    assert duty.coins == []
    assert duty.ksbs == []


def test_update_duty_returns_none_on_error(mocker):
    mocker.patch("models.duty.api_session.patch", side_effect=requests.RequestException("Error"))
    duty = Duty.update_duty("D5", name="Fail Update")
    assert duty is None


# DELETE DUTY
def test_delete_duty_success(mock_api_session_delete):
    mock_api_session_delete()
    result = Duty.delete_duty("D1")
    assert result is True


def test_delete_duty_returns_false_on_error(mocker):
    mocker.patch("models.duty.api_session.delete", side_effect=requests.RequestException("Error"))
    result = Duty.delete_duty("D99")
    assert result is False