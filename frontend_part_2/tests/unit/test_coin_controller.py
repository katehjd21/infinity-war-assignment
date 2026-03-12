import pytest
from controllers.coin_controller import CoinController
from models.coin import Coin

@pytest.fixture
def coin_controller():
    return CoinController()


# FETCH ALL COINS
def test_coin_controller_calls_model_method_fetches_coins(mocker, coin_controller, mocked_coins):
    mock_model = mocker.patch(
        "models.coin.Coin.fetch_coins_from_backend",
        return_value=mocked_coins
    )
    result = coin_controller.fetch_all_coins()
    mock_model.assert_called_once()
    assert result == mocked_coins


def test_coin_controller_fetch_all_coins_returns_empty_if_no_coins(mocker, coin_controller):
    mocker.patch("models.coin.Coin.fetch_coins_from_backend", return_value=[])
    result = coin_controller.fetch_all_coins()
    assert result == []


# FETCH COIN BY ID
def test_coin_controller_can_fetch_coin_by_id(mocker, coin_controller, mocked_coin):
    mock_fetch = mocker.patch(
        "models.coin.Coin.fetch_coin_from_backend_by_id",
        return_value=mocked_coin
    )
    result = coin_controller.fetch_coin_by_id(mocked_coin.id)
    mock_fetch.assert_called_once_with(mocked_coin.id)
    assert result == mocked_coin


def test_coin_controller_fetch_coin_by_id_not_found(mocker, coin_controller):
    mocker.patch("models.coin.Coin.fetch_coin_from_backend_by_id", return_value=None)
    result = coin_controller.fetch_coin_by_id("non-existent-id")
    assert result is None


# TOGGLE COIN COMPLETION
def test_coin_controller_toggle_coin_complete(mocker, coin_controller, mocked_coin):
    toggled_coin = Coin(mocked_coin.name, mocked_coin.id, duties=mocked_coin.duties, completed=not mocked_coin.completed)
    mocker.patch("models.coin.Coin.toggle_complete", return_value=toggled_coin)
    result = coin_controller.toggle_coin_complete(mocked_coin.id)
    assert result.completed != mocked_coin.completed


def test_coin_controller_toggle_coin_complete_failure(mocker, coin_controller):
    mocker.patch("models.coin.Coin.toggle_complete", return_value=None)
    result = coin_controller.toggle_coin_complete("non-existent-id")
    assert result is None


# CREATE COIN
def test_coin_controller_create_coin_returns_tuple(mocker, coin_controller, mocked_coin):
    mocker.patch(
        "models.coin.Coin.create_coin",
        return_value=(mocked_coin, None)
    )
    result = coin_controller.create_coin("Automate", duty_codes=["D1", "D2"], completed=True)
    assert isinstance(result, tuple)
    coin, error = result
    assert coin == mocked_coin
    assert error is None


def test_coin_controller_create_coin_failure_returns_tuple(mocker, coin_controller):
    mocker.patch(
        "models.coin.Coin.create_coin",
        return_value=(None, "Server error")
    )
    result = coin_controller.create_coin("Invalid Coin", duty_codes=["D1"])
    coin, error = result
    assert coin is None
    assert error == "Server error"


# UPDATE COIN
def test_coin_controller_update_coin_returns_tuple(mocker, coin_controller, mocked_coin):
    updated_coin = Coin(mocked_coin.name, mocked_coin.id, duties=mocked_coin.duties, completed=True)
    mocker.patch(
        "models.coin.Coin.update_coin",
        return_value=(updated_coin, None)
    )
    result = coin_controller.update_coin(coin_id=mocked_coin.id, name="Updated Name", duty_codes=["D1", "D2"], completed=True)
    assert isinstance(result, tuple)
    coin, error = result
    assert coin == updated_coin
    assert error is None


def test_coin_controller_update_coin_failure_returns_tuple(mocker, coin_controller):
    mocker.patch(
        "models.coin.Coin.update_coin",
        return_value=(None, "Server error")
    )
    result = coin_controller.update_coin("non-existent-id", name="Fail Update")
    coin, error = result
    assert coin is None
    assert error == "Server error"


# DELETE COIN
def test_coin_controller_delete_coin_success(mocker, coin_controller):
    mocker.patch("models.coin.Coin.delete_coin", return_value=True)
    result = coin_controller.delete_coin("11111111-1111-1111-1111-111111111111")
    assert result is True


def test_coin_controller_delete_coin_failure(mocker, coin_controller):
    mocker.patch("models.coin.Coin.delete_coin", return_value=False)
    result = coin_controller.delete_coin("non-existent-id")
    assert result is False