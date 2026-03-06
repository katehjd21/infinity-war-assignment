from models.coin import Coin
from unittest.mock import Mock
import pytest
import requests

@pytest.fixture
def mock_api_session_get(mocker):
    def _mock(response_data):
        mock_response = Mock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mocker.patch("models.coin.api_session.get", return_value=mock_response)
    return _mock


@pytest.fixture
def mock_api_session_post(mocker):
    def _mock(response_data):
        mock_response = Mock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        patched_mock = mocker.patch("models.coin.api_session.post", return_value=mock_response)
        return patched_mock
    return _mock


@pytest.fixture
def mock_api_session_patch(mocker):
    def _mock(response_data):
        mock_response = Mock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        patched_mock = mocker.patch("models.coin.api_session.patch", return_value=mock_response)
        return patched_mock
    return _mock


@pytest.fixture
def mock_api_session_delete(mocker):
    def _mock(return_value=True):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        patched_mock = mocker.patch("models.coin.api_session.delete", return_value=mock_response)
        return patched_mock
    return _mock


# FETCH ALL COINS
def test_fetch_all_coins_from_backend(mocked_coins_response, mock_api_session_get):
    mock_api_session_get(mocked_coins_response)
    coins = Coin.fetch_coins_from_backend()
    assert len(coins) == len(mocked_coins_response)

    coins_by_id = {coin.id: coin for coin in coins}
    for response in mocked_coins_response:
        coin = coins_by_id[response["id"]]
        assert coin.name == response["name"]
        assert coin.duties == response.get("duties", [])
        assert coin.completed == response.get("completed", False)


def test_fetch_empty_coins_list_from_backend(mock_api_session_get):
    mock_api_session_get([])
    coins = Coin.fetch_coins_from_backend()
    assert coins == []


def test_fetch_all_coins_raises_exception(mocker):
    mocker.patch(
        "models.coin.api_session.get",
        side_effect=requests.RequestException("Network Error")
    )
    coins = Coin.fetch_coins_from_backend()
    assert coins == []


# FETCH COIN BY ID
def test_fetch_coin_by_id_with_duties_and_completed(mock_api_session_get):
    response_data = {
        "name": "Automate",
        "id": "11111111-1111-1111-1111-111111111111",
        "duties": [{"code": "D1", "name": "Duty 1", "description": "Duty 1 Description"}],
        "completed": True
    }
    mock_api_session_get(response_data)
    coin = Coin.fetch_coin_from_backend_by_id(response_data["id"])
    assert coin.name == response_data["name"]
    assert coin.id == response_data["id"]
    assert coin.duties == response_data["duties"]
    assert coin.completed is True


def test_fetch_coin_by_id_defaults_completed_to_false(mock_api_session_get):
    response_data = {"name": "Assemble", "id": "55555555-5555-5555-5555-555555555555"}
    mock_api_session_get(response_data)
    coin = Coin.fetch_coin_from_backend_by_id(response_data["id"])
    assert coin.completed is False
    assert coin.duties == []


def test_fetch_coin_by_id_returns_none_on_error(mocker):
    mocker.patch(
        "models.coin.api_session.get",
        side_effect=requests.RequestException("Network Error")
    )
    coin = Coin.fetch_coin_from_backend_by_id("invalid_coin_id")
    assert coin is None


# TOGGLE COIN COMPLETION
def test_toggle_coin_complete_from_false_to_true(mock_api_session_post):
    response_data = {
        "id": "55555555-5555-5555-5555-555555555555",
        "name": "Automate",
        "completed": True,
        "duties": []
    }
    mock_post = mock_api_session_post(response_data)
    coin = Coin.toggle_complete("55555555-5555-5555-5555-555555555555")
    expected_url = f"http://localhost:5000/coins/55555555-5555-5555-5555-555555555555/complete"
    mock_post.assert_called_with(expected_url)
    assert isinstance(coin, Coin)
    assert coin.completed is True


def test_toggle_coin_complete_from_true_to_false(mock_api_session_post):
    response_data = {
        "id": "55555555-5555-5555-5555-555555555555",
        "name": "Automate",
        "completed": False,
        "duties": []
    }
    mock_post = mock_api_session_post(response_data)
    coin = Coin.toggle_complete("55555555-5555-5555-5555-555555555555")
    expected_url = f"http://localhost:5000/coins/55555555-5555-5555-5555-555555555555/complete"
    mock_post.assert_called_with(expected_url)
    assert isinstance(coin, Coin)
    assert coin.completed is False


def test_toggle_coin_complete_failure(mocker):
    mocker.patch(
        "models.coin.api_session.post",
        side_effect=requests.RequestException("Error")
    )
    result = Coin.toggle_complete("invalid_id")
    assert result is None


# CREATE COIN
def test_create_coin_with_duties_success(mock_api_session_post):
    response_data = {
        "name": "Newly Created Coin",
        "id": "22222222-2222-2222-2222-222222222222",
        "duties": ["D2"],
        "completed": False
    }
    mock_post = mock_api_session_post(response_data)
    coin = Coin.create_coin("Newly Created Coin", duty_codes=["D2"])
    expected_url = "http://localhost:5000/v3/coins"
    mock_post.assert_called_with(expected_url, json={"name": "Newly Created Coin", "duty_codes": ["D2"]})
    assert coin.name == response_data["name"]
    assert coin.duties == response_data["duties"]
    assert coin.completed is False


def test_create_coin_without_duties_success(mock_api_session_post):
    response_data = {
        "name": "Newly Created Coin",
        "id": "22222222-2222-2222-2222-222222222222",
        "duties": [],
        "completed": False
    }
    mock_post = mock_api_session_post(response_data)
    coin = Coin.create_coin("Newly Created Coin", duty_codes=[])
    expected_url = "http://localhost:5000/v3/coins"
    mock_post.assert_called_with(expected_url, json={"name": "Newly Created Coin", "duty_codes": []})
    assert coin.name == response_data["name"]
    assert coin.duties == []
    assert coin.completed is False


def test_create_coin_returns_none_on_error(mocker):
    mocker.patch(
        "models.coin.api_session.post",
        side_effect=requests.RequestException("Network Error")
    )
    coin = Coin.create_coin("Failed Coin")
    assert coin is None


# UPDATE COIN
def test_update_coin_success(mock_api_session_patch):
    response_data = {
        "name": "Another coin name Coin",
        "id": "33333333-3333-3333-3333-333333333333",
        "duties": ["D3"],
        "completed": True
    }
    mock_patch = mock_api_session_patch(response_data)
    coin = Coin.update_coin(
        coin_id=response_data["id"],
        name="Updated Coin",
        duty_codes=["D3"]
    )
    expected_url = f"http://localhost:5000/v3/coins/{response_data['id']}"
    mock_patch.assert_called_with(expected_url, json={"name": "Updated Coin", "duty_codes": ["D3"]})
    assert coin.name == response_data["name"]
    assert coin.duties == response_data["duties"]
    assert coin.completed is True


def test_update_coin_name_only(mock_api_session_patch):
    response_data = {
        "name": "Updated Name",
        "id": "33333333-3333-3333-3333-333333333333",
        "duties": [],
        "completed": False
    }

    mock_patch = mock_api_session_patch(response_data)

    coin = Coin.update_coin(
        coin_id=response_data["id"],
        name="Updated Name"
    )

    mock_patch.assert_called_once_with(
        f"http://localhost:5000/v3/coins/{response_data['id']}",
        json={"name": "Updated Name"}
    )

    assert coin.name == "Updated Name"


def test_update_coin_duties_only(mock_api_session_patch):
    response_data = {
        "name": "Automation",
        "id": "33333333-3333-3333-3333-333333333333",
        "duties": ["D1"],
        "completed": False
    }

    mock_patch = mock_api_session_patch(response_data)

    coin = Coin.update_coin(
        coin_id=response_data["id"],
        duty_codes=["D1"]
    )

    mock_patch.assert_called_once_with(
        f"http://localhost:5000/v3/coins/{response_data['id']}",
        json={"duty_codes": ["D1"]}
    )

    assert coin.duties == ["D1"]


def test_update_coin_returns_none_on_error(mocker):
    mocker.patch(
        "models.coin.api_session.patch",
        side_effect=requests.RequestException("Network Error")
    )
    coin = Coin.update_coin("invalid_id", name="Failed Update Coin")
    assert coin is None


# DELETE COIN
def test_delete_coin_success(mock_api_session_delete):

    mock_delete = mock_api_session_delete()

    result = Coin.delete_coin("44444444-4444-4444-4444-444444444444")

    mock_delete.assert_called_once_with(
        "http://localhost:5000/v2/coins/44444444-4444-4444-4444-444444444444"
    )

    assert result is True


def test_delete_coin_returns_false_on_error(mocker):
    mocker.patch(
        "models.coin.api_session.delete",
        side_effect=requests.RequestException("Network Error")
    )
    result = Coin.delete_coin("invalid_id")
    assert result is False