import pytest
from controllers.coin_controller import CoinController

@pytest.fixture
def coin_controller():
    return CoinController()

def test_coin_controller_can_fetch_all_coins(mocker, coin_controller, mocked_coins):
    mocker.patch("models.coin.Coin.fetch_coins_from_backend", return_value=mocked_coins)
    fetched_coins = coin_controller.fetch_all_coins()
    
    assert fetched_coins == mocked_coins
    assert fetched_coins[0].name == "Automate"
    assert fetched_coins[1].name == "Houston"
    assert fetched_coins[2].id == "33333333-3333-3333-3333-333333333333"


def test_coin_controller_fetch_all_coins_returns_empty_if_no_coins(mocker, coin_controller):
    mocker.patch("models.coin.Coin.fetch_coins_from_backend", return_value=[])
    fetched_coins = coin_controller.fetch_all_coins()
    
    assert fetched_coins == []


def test_coin_controller_can_fetch_coin_by_id(mocker, coin_controller, mocked_coins):
    mocker.patch("models.coin.Coin.fetch_coin_from_backend_by_id",  return_value=mocked_coins[0])
    fetched_coin = coin_controller.fetch_coin_by_id("11111111-1111-1111-1111-111111111111")

    assert fetched_coin.name == "Automate"
    assert fetched_coin.id == "11111111-1111-1111-1111-111111111111"


def test_coin_controller_fetch_coin_by_id_coin_not_found(mocker, coin_controller):
    mocker.patch("models.coin.Coin.fetch_coin_from_backend_by_id", return_value=None)
    fetched_coin = coin_controller.fetch_coin_by_id("non-existent-id")
    
    assert fetched_coin is None


def test_coin_controller_calls_model_method(mocker, coin_controller, mocked_coins):
    mock_model = mocker.patch("models.coin.Coin.fetch_coins_from_backend", return_value=mocked_coins)
    coin_controller.fetch_all_coins()
    
    assert mock_model.call_count == 1