from models.coin import Coin
from unittest.mock import Mock
import pytest
import requests

@pytest.fixture
def mock_requests_get(mocker):
    def _mock(response_data):
        mock_response = Mock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mocker.patch("models.coin.requests.get", return_value=mock_response)
    return _mock


def test_coin_has_name(mocked_coin):
    assert mocked_coin.name == "Automate"


def test_fetch_all_coins_from_backend(mocked_coins_response, mock_requests_get):
    mock_requests_get(mocked_coins_response)

    coins = Coin.fetch_coins_from_backend()

    assert len(coins) == len(mocked_coins_response)

    coins_by_id = {coin.id: coin for coin in coins}

    for response in mocked_coins_response:
        coin = coins_by_id[response["id"]]
        assert coin.name == response["name"]


def test_fetch_empty_coins_list_from_backend(mock_requests_get):
    mock_requests_get([])

    coins = Coin.fetch_coins_from_backend()

    assert coins == []


def test_fetch_all_coins_raises_exception(mocker):
    mocker.patch(
        "models.coin.requests.get",
        side_effect=requests.RequestException("Network Error")
    )
    coins = Coin.fetch_coins_from_backend()
    assert coins == []


def test_coin_fetch_coin_by_id_with_duties_from_backend(mock_requests_get, mocked_coins_response):
    mocked_coin_response = mocked_coins_response[0]

    mock_requests_get(mocked_coin_response)

    coin = Coin.fetch_coin_from_backend_by_id(mocked_coin_response["id"])

    assert coin.name == mocked_coin_response["name"]
    assert coin.id == mocked_coin_response["id"]
    assert coin.duties == mocked_coin_response["duties"]


def test_coin_fetch_coin_by_id_with_missing_duties_from_backend(mock_requests_get):
    response_data = {"name": "Assemble", "id": "55555555-5555-5555-5555-555555555555"}

    mock_requests_get(response_data)

    coin = Coin.fetch_coin_from_backend_by_id(response_data["id"])

    assert coin.duties == []


def test_fetch_coin_by_id_returns_none_on_error(mock_requests_get):
    mock_requests_get.side_effect = Exception("Network error")
    coin = Coin.fetch_coin_from_backend_by_id("invalid_coin_id")
    assert coin is None