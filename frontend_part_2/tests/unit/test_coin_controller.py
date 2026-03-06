import pytest
from controllers.coin_controller import CoinController
from models.coin import Coin

@pytest.fixture
def coin_controller():
    return CoinController()


def test_coin_controller_calls_model_method(mocker, coin_controller, mocked_coins):
    mock_model = mocker.patch("models.coin.Coin.fetch_coins_from_backend", return_value=mocked_coins)
    coin_controller.fetch_all_coins()
    
    assert mock_model.call_count == 1
    

# FETCH ALL COINS
def test_coin_controller_can_fetch_all_coins(mocker, coin_controller, mocked_coins):
    mocker.patch("models.coin.Coin.fetch_coins_from_backend", return_value=mocked_coins)
    fetched_coins = coin_controller.fetch_all_coins()
    
    assert fetched_coins == mocked_coins


def test_coin_controller_fetch_all_coins_returns_empty_if_no_coins(mocker, coin_controller):
    mocker.patch("models.coin.Coin.fetch_coins_from_backend", return_value=[])
    fetched_coins = coin_controller.fetch_all_coins()
    
    assert fetched_coins == []


# FETCH COIN BY ID
def test_coin_controller_can_fetch_coin_by_id(mocker, coin_controller, mocked_coin):
    mocker.patch("models.coin.Coin.fetch_coin_from_backend_by_id",  return_value=mocked_coin)
    fetched_coin = coin_controller.fetch_coin_by_id("11111111-1111-1111-1111-111111111111")

    assert fetched_coin.name == "Automate"
    assert fetched_coin.id == "11111111-1111-1111-1111-111111111111"

    expected_duties = [
                {"code": "D1", "name": "Duty 1", "description": "Duty 1 Description"},
                {"code": "D2", "name": "Duty 2", "description": "Duty 2 Description"},
            ]
    assert fetched_coin.duties == expected_duties


def test_coin_controller_fetch_coin_by_id_coin_not_found(mocker, coin_controller):
    mocker.patch("models.coin.Coin.fetch_coin_from_backend_by_id", return_value=None)
    fetched_coin = coin_controller.fetch_coin_by_id("non-existent-id")
    
    assert fetched_coin is None


# TOGGLE COIN COMPLETION
def test_coin_controller_can_toggle_coin_completion_false_to_true(mocker, coin_controller):
    original_coin = Coin(
        "Automate",
        "11111111-1111-1111-1111-111111111111",
        duties=[
            {"code": "D1", "name": "Duty 1", "description": "Duty 1 Description"},
            {"code": "D2", "name": "Duty 2", "description": "Duty 2 Description"},
        ],
        completed=False
    )

    toggled_coin = Coin(
        original_coin.name,
        original_coin.id,
        duties=original_coin.duties,
        completed=True
    )

    mocker.patch("models.coin.Coin.toggle_complete", return_value=toggled_coin)

    result = coin_controller.toggle_coin_complete(original_coin.id)

    assert result is not None
    assert isinstance(result, Coin)
    assert result.id == original_coin.id
    assert result.completed is True


def test_coin_controller_can_toggle_coin_completion_true_to_false(mocker, coin_controller):
    original_coin = Coin(
        "Automate",
        "11111111-1111-1111-1111-111111111111",
        duties=[
            {"code": "D1", "name": "Duty 1", "description": "Duty 1 Description"},
            {"code": "D2", "name": "Duty 2", "description": "Duty 2 Description"},
        ],
        completed=True
    )

    toggled_coin = Coin(
        original_coin.name,
        original_coin.id,
        duties=original_coin.duties,
        completed=False
    )

    mocker.patch("models.coin.Coin.toggle_complete", return_value=toggled_coin)

    result = coin_controller.toggle_coin_complete(original_coin.id)

    assert result is not None
    assert isinstance(result, Coin)
    assert result.id == original_coin.id
    assert result.completed is False


def test_coin_controller_toggle_coin_completion_failure(mocker, coin_controller):
    mocker.patch("models.coin.Coin.toggle_complete", return_value=None)

    result = coin_controller.toggle_coin_complete("non-existent-id")

    assert result is None


# CREATE COIN
def test_coin_controller_can_create_coin(mocker, coin_controller, mocked_coin):
    mocker.patch(
        "models.coin.Coin.create_coin",
        return_value=mocked_coin
    )

    new_coin = coin_controller.create_coin("Automate", duty_codes=["D1", "D2"])

    assert new_coin is not None
    assert isinstance(new_coin, Coin)
    assert new_coin.name == "Automate"
    assert new_coin.duties == mocked_coin.duties
    assert new_coin.completed == mocked_coin.completed


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

    mocker.patch(
        "models.coin.Coin.update_coin",
        return_value=updated_coin
    )

    result = coin_controller.update_coin(
        coin_id=mocked_coin.id,
        name="Updated Name",
        duty_codes=["D1", "D2"]
    )

    assert result is not None
    assert isinstance(result, Coin)
    assert result.id == mocked_coin.id
    assert result.completed is True


def test_coin_controller_update_coin_returns_none_on_failure(mocker, coin_controller):
    mocker.patch(
        "models.coin.Coin.update_coin",
        return_value=None
    )

    result = coin_controller.update_coin("non-existent-id", name="Fail Update")

    assert result is None


# DELETE COIN
def test_coin_controller_can_delete_coin_success(mocker, coin_controller):
    mocker.patch("models.coin.Coin.delete_coin", return_value=True)

    result = coin_controller.delete_coin("11111111-1111-1111-1111-111111111111")

    assert result is True


def test_coin_controller_delete_coin_failure(mocker, coin_controller):
    mocker.patch("models.coin.Coin.delete_coin", return_value=False)

    result = coin_controller.delete_coin("non-existent-id")

    assert result is False