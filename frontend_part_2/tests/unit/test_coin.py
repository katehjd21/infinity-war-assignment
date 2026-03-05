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


def test_coin_has_name(mocked_coin):
    assert mocked_coin.name == "Automate"

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
    response_data = {
        "name": "Assemble",
        "id": "55555555-5555-5555-5555-555555555555"
    }

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