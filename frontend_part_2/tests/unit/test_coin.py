import pytest
from models.coin import Coin
from unittest.mock import Mock

@pytest.fixture
def coin():
    return Coin("Houston")


def test_coin_has_name(coin):
    assert coin.name == "Houston"


def test_coin_can_fetch_coin_name_from_backend(mocker):
    mocked_response = [
        {"name": "Automate", "id": "11111111-1111-1111-1111-111111111111"},
        {"name": "Houston", "id": "22222222-2222-2222-2222-222222222222"},
        {"name": "Security", "id": "33333333-3333-3333-3333-333333333333"},
        {"name": "GoingDeeper", "id": "44444444-4444-4444-4444-444444444444"},
        {"name": "Assemble", "id": "55555555-5555-5555-5555-555555555555"},
    ]

    mock_response = Mock()
    mock_response.json.return_value = mocked_response
    mock_response.raise_for_status.return_value = None 

    mocker.patch("models.coin.requests.get", return_value=mock_response)

    coins = Coin.fetch_coins_from_backend()
    coin_names = [coin.name for coin in coins]

    assert coin_names == ["Automate", "Houston", "Security", "GoingDeeper", "Assemble"]


def test_coin_can_fetch_coin_ids_from_backend(mocker):
    mocked_response = [
        {"name": "Automate", "id": "11111111-1111-1111-1111-111111111111"},
        {"name": "Houston", "id": "22222222-2222-2222-2222-222222222222"},
    ]

    mock_response = Mock()
    mock_response.json.return_value = mocked_response
    mock_response.raise_for_status.return_value = None

    mocker.patch("models.coin.requests.get", return_value=mock_response)

    coins = Coin.fetch_coins_from_backend()
    coin_ids = [coin.id for coin in coins]

    assert coin_ids == ["11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222"]


def test_coin_fetch_empty_coin_list_from_backend(mocker):
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_response.raise_for_status.return_value = None

    mocker.patch("models.coin.requests.get", return_value=mock_response)

    coins = Coin.fetch_coins_from_backend()
    assert coins == []


def test_coin_can_fetch_single_coin_by_id(mocker):
    mocked_response = {"name": "Automate", "id": "11111111-1111-1111-1111-111111111111"}
    
    mock_response = Mock()
    mock_response.json.return_value = mocked_response
    mock_response.raise_for_status.return_value = None

    mocker.patch("models.coin.requests.get", return_value=mock_response)

    coin = Coin.fetch_coin_from_backend_by_id("11111111-1111-1111-1111-111111111111")
    
    assert coin.name == "Automate"
    assert coin.id == "11111111-1111-1111-1111-111111111111"

def test_coin_fetch_coin_with_duties(mocker):
    mocked_response = {
        "name": "Automate",
        "id": "11111111-1111-1111-1111-111111111111",
        "duties": [
            {
                "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "code": "D1",
                "name": "Duty 1",
                "description": "Duty 1 Description"
            },
            {
                "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "code": "D2",
                "name": "Duty 2",
                "description": "Duty 2 Description"
            }
        ]
    }

    mock_response = Mock()
    mock_response.json.return_value = mocked_response
    mock_response.raise_for_status.return_value = None

    mocker.patch("models.coin.requests.get", return_value=mock_response)

    coin = Coin.fetch_coin_from_backend_by_id("11111111-1111-1111-1111-111111111111")

    assert coin.name == "Automate"
    assert coin.id == "11111111-1111-1111-1111-111111111111"

    assert len(coin.duties) == 2
    assert coin.duties[0]["id"] == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    assert coin.duties[0]["code"] == "D1"
    assert coin.duties[0]["name"] == "Duty 1"
    assert coin.duties[0]["description"] == "Duty 1 Description"
    assert coin.duties[1]["id"] == "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    assert coin.duties[1]["code"] == "D2"
    assert coin.duties[1]["name"] == "Duty 2"
    assert coin.duties[1]["description"] == "Duty 2 Description"


def test_coin_fetch_coin_with_no_duties(mocker):
    mocked_response = {
        "name": "Security",
        "id": "33333333-3333-3333-3333-333333333333",
        "duties": []
    }

    mock_response = Mock()
    mock_response.json.return_value = mocked_response
    mock_response.raise_for_status.return_value = None

    mocker.patch("models.coin.requests.get", return_value=mock_response)

    coin = Coin.fetch_coin_from_backend_by_id("33333333-3333-3333-3333-333333333333")

    assert coin.name == "Security"
    assert coin.duties == []