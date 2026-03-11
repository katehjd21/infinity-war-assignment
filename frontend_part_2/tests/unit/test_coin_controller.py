import pytest
from controllers.coin_controller import CoinController
from models.coin import Coin

@pytest.fixture
def coin_controller():
    return CoinController()



def test_controller_handles_model_exception(mocker, coin_controller):
    mocker.patch(
        "models.coin.Coin.fetch_coins_from_backend",
        side_effect=Exception("Backend error")
    )

    with pytest.raises(Exception):
        coin_controller.fetch_all_coins()
    

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
    fetched_coins = coin_controller.fetch_all_coins()
    
    assert fetched_coins == []


# FETCH COIN BY ID
def test_coin_controller_can_fetch_coin_by_id(mocker, coin_controller, mocked_coin):

    mock_fetch = mocker.patch(
        "models.coin.Coin.fetch_coin_from_backend_by_id",
        return_value=mocked_coin
    )

    fetched_coin = coin_controller.fetch_coin_by_id(mocked_coin.id)

    mock_fetch.assert_called_once_with(mocked_coin.id)

    assert fetched_coin == mocked_coin


def test_coin_controller_fetch_coin_by_id_coin_not_found(mocker, coin_controller):
    mocker.patch("models.coin.Coin.fetch_coin_from_backend_by_id", return_value=None)
    fetched_coin = coin_controller.fetch_coin_by_id("non-existent-id")
    
    assert fetched_coin is None


# TOGGLE COIN COMPLETION
def test_coin_controller_toggle_coin_complete(mocker, coin_controller, mocked_coin):

    toggled_coin = Coin(
        mocked_coin.name,
        mocked_coin.id,
        duties=mocked_coin.duties,
        completed=not mocked_coin.completed
    )

    mock_toggle = mocker.patch(
        "models.coin.Coin.toggle_complete",
        return_value=toggled_coin
    )

    result = coin_controller.toggle_coin_complete(mocked_coin.id)

    mock_toggle.assert_called_once_with(mocked_coin.id)

    assert result.completed != mocked_coin.completed


def test_coin_controller_toggle_coin_completion_failure(mocker, coin_controller):
    mocker.patch("models.coin.Coin.toggle_complete", return_value=None)

    result = coin_controller.toggle_coin_complete("non-existent-id")

    assert result is None


# CREATE COIN
def test_coin_controller_can_create_coin(mocker, coin_controller, mocked_coin):

    mock_create = mocker.patch(
        "models.coin.Coin.create_coin",
        return_value=mocked_coin
    )

    new_coin = coin_controller.create_coin("Automate", duty_codes=["D1", "D2"], completed=True)

    mock_create.assert_called_once_with("Automate", ["D1", "D2"], True)

    assert new_coin == mocked_coin


def test_coin_controller_create_coin_returns_none_on_failure(mocker, coin_controller):
    mocker.patch(
        "models.coin.Coin.create_coin",
        return_value=None
    )

    result = coin_controller.create_coin("Invalid Coin", duty_codes=["D1"])

    assert result is None


# UPDATE COIN
def test_coin_controller_can_update_coin(mocker, coin_controller, mocked_coin):
    updated_coin = Coin(
        mocked_coin.name,
        mocked_coin.id,
        duties=mocked_coin.duties,
        completed=True
    )

    mock_update = mocker.patch(
        "models.coin.Coin.update_coin",
        return_value=updated_coin
    )

    result = coin_controller.update_coin(
        coin_id=mocked_coin.id,
        name="Updated Name",
        duty_codes=["D1", "D2"],
        completed=True
    )

    mock_update.assert_called_once_with(
        mocked_coin.id,
        "Updated Name",
        ["D1", "D2"],
        True
    )

    assert result == updated_coin


def test_coin_controller_update_coin_returns_none_on_failure(mocker, coin_controller):
    mocker.patch(
        "models.coin.Coin.update_coin",
        return_value=None
    )

    result = coin_controller.update_coin("non-existent-id", name="Fail Update")

    assert result is None


# DELETE COIN
def test_coin_controller_can_delete_coin_success(mocker, coin_controller):

    mock_delete = mocker.patch(
        "models.coin.Coin.delete_coin",
        return_value=True
    )

    result = coin_controller.delete_coin("11111111-1111-1111-1111-111111111111")

    mock_delete.assert_called_once_with("11111111-1111-1111-1111-111111111111")

    assert result is True


def test_coin_controller_delete_coin_failure(mocker, coin_controller):
    mocker.patch("models.coin.Coin.delete_coin", return_value=False)

    result = coin_controller.delete_coin("non-existent-id")

    assert result is False