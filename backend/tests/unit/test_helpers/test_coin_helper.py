import pytest
import uuid
from helpers.coin import CoinHelper
from models import Coin, DutyCoin
from werkzeug.exceptions import HTTPException, BadRequest


# TEST VALIDATE COIN NAME
def test_validate_coin_name_strips_and_returns_name():
    name = "  Coin Name  "
    result = CoinHelper.validate_coin_name(name, check_exists=False)
    assert result == "Coin Name"


def test_validate_coin_name_empty_raises_abort():
    with pytest.raises(HTTPException) as e:
        CoinHelper.validate_coin_name("   ", check_exists=False)
    assert "Coin name cannot be empty" in str(e.value)


def test_validate_coin_name_duplicate_raises_abort(coins):
    with pytest.raises(HTTPException) as e:
        CoinHelper.validate_coin_name(coins[0].name, check_exists=True)
    assert "Coin already exists" in str(e.value)


# TEST GET COIN BY ID
def test_get_coin_by_id_returns_coin(coin):
    fetched = CoinHelper.get_coin_by_id(str(coin.id))
    assert fetched.id == coin.id


def test_get_coin_by_id_invalid_uuid_raises_abort():
    with pytest.raises(HTTPException) as e:
        CoinHelper.get_coin_by_id("not-a-uuid")
    assert "Invalid Coin ID: not-a-uuid. Coin ID must be a UUID (non-integer)." in str(e.value)


def test_get_coin_by_id_nonexistent_raises_abort():
    random_uuid = str(uuid.uuid4())
    with pytest.raises(HTTPException) as e:
        CoinHelper.get_coin_by_id(random_uuid)
    assert "Coin not found" in str(e.value)


# TEST ATTACH DUTIES
def test_attach_duties_adds_links(coin, duties):
    CoinHelper.attach_duties(coin, [duties[0].code])
    assert DutyCoin.select().where(DutyCoin.coin == coin, DutyCoin.duty == duties[0]).exists()


def test_attach_duties_invalid_duty_raises_abort(coin):
    with pytest.raises(BadRequest) as e:
        CoinHelper.attach_duties(coin, ["NOT FOUND"])
    
    assert "Invalid duty codes: NOT FOUND" in str(e.value)


def test_attach_duties_non_list_raises_abort(coin):
    with pytest.raises(HTTPException) as e:
        CoinHelper.attach_duties(coin, "D1")
    assert "'duty_codes' must be a list" in str(e.value)


# TEST CREATE COIN
def test_create_coin_without_duties():
    data = {"name": "New Coin"}
    coin = CoinHelper.create_coin(data, with_duties=False)
    assert coin.name == "New Coin"
    assert Coin.select().where(Coin.id == coin.id).exists()


def test_create_coin_with_duties(duties):
    data = {"name": "Coin With Duties", "duty_codes": [duty.code for duty in duties]}
    coin = CoinHelper.create_coin(data, with_duties=True)
    linked_duties = [dc.duty.code for dc in DutyCoin.select().where(DutyCoin.coin == coin)]
    for duty in duties:
        assert duty.code in linked_duties


def test_create_coin_missing_name_raises_abort():
    with pytest.raises(HTTPException) as excinfo:
        CoinHelper.create_coin({}, with_duties=False)
    assert "Missing 'name' key" in str(excinfo.value)


def test_create_coin_invalid_duty_code_raises_abort():
    data = {"name": "Coin Invalid Duty", "duty_codes": ["FAKE DUTY CODE"]}
    with pytest.raises(HTTPException) as e:
        CoinHelper.create_coin(data, with_duties=True)
    assert "Invalid duty codes: FAKE DUTY CODE" in str(e.value)


def test_create_coin_with_completed_true():
    data = {"name": "Completed Coin", "completed": True}
    coin = CoinHelper.create_coin(data, with_duties=False)

    assert coin.completed is True


def test_create_coin_with_completed_false():
    data = {"name": "Incomplete Coin", "completed": False}
    coin = CoinHelper.create_coin(data, with_duties=False)

    assert coin.completed is False


def test_create_coin_invalid_completed_type_raises_abort():
    data = {"name": "Bad Coin", "completed": "yes"}
    with pytest.raises(HTTPException) as e:
        CoinHelper.create_coin(data, with_duties=False)

    assert "'completed' must be a boolean" in str(e.value)


def test_create_coin_with_empty_duty_codes_list():
    data = {"name": "Empty Duties Coin", "duty_codes": []}
    coin = CoinHelper.create_coin(data, with_duties=True)
    assert coin.name == "Empty Duties Coin"
    linked_duties = list(DutyCoin.select().where(DutyCoin.coin == coin))
    assert linked_duties == []


# TEST TOGGLE COMPLETE COIN
def test_toggle_complete_coin_sets_flag():
    coin = Coin.create(name="Test Coin")
    assert coin.completed is False

    result = CoinHelper.toggle_complete_coin(str(coin.id))
    assert result is True

    coin = Coin.get_by_id(coin.id)
    assert coin.completed is True

    result = CoinHelper.toggle_complete_coin(str(coin.id))
    assert result is False


def test_toggle_complete_coin_invalid_id():
    with pytest.raises(HTTPException) as e:
        CoinHelper.toggle_complete_coin("invalid-uuid")
    assert "Invalid Coin ID" in str(e.value)

def test_toggle_complete_coin_nonexistent():
    fake_id = "11111111-1111-1111-1111-111111111111"
    with pytest.raises(HTTPException) as e:
        CoinHelper.toggle_complete_coin(fake_id)
    assert "Coin not found" in str(e.value)


# TEST UPDATE COIN
def test_update_coin_name_only(coin):
    updated = CoinHelper.update_coin(str(coin.id), {"name": "Updated Coin Name"})
    assert updated.name == "Updated Coin Name"

def test_update_coin_duties_only(coin, duties):
    CoinHelper.update_coin(str(coin.id), {"duty_codes": [duties[1].code]})
    linked = [dc.duty.code for dc in DutyCoin.select().where(DutyCoin.coin == coin)]
    assert linked == [duties[1].code]

def test_update_coin_missing_name_required(coin):
    with pytest.raises(HTTPException) as e:
        CoinHelper.update_coin(str(coin.id), {}, require_name=True)
    assert "Missing 'name' key" in str(e.value)


def test_update_coin_sets_completed_true(coin):
    updated = CoinHelper.update_coin(str(coin.id), {"completed": True})
    assert updated.completed is True


def test_update_coin_sets_completed_false(coin):
    coin.completed = True
    coin.save()

    updated = CoinHelper.update_coin(str(coin.id), {"completed": False})
    assert updated.completed is False


def test_update_coin_invalid_completed_type_raises_abort(coin):
    with pytest.raises(HTTPException) as e:
        CoinHelper.update_coin(str(coin.id), {"completed": "nope"})

    assert "'completed' must be a boolean" in str(e.value)


def test_update_coin_empty_body_raises_abort(coin):
    with pytest.raises(HTTPException) as e:
        CoinHelper.update_coin(str(coin.id), {})
    assert "Request body is empty" in str(e.value)


def test_update_coin_invalid_duty_code_raises_abort(coin):
    with pytest.raises(BadRequest) as e:
        CoinHelper.update_coin(str(coin.id), {"duty_codes": ["INVALID"]})
    
    assert "Invalid duty codes: INVALID" in str(e.value)


# TEST DELETE COIN
def test_delete_coin_removes_coin(coin):
    CoinHelper.delete_coin(str(coin.id))
    assert not Coin.select().where(Coin.id == coin.id).exists()

def test_delete_coin_invalid_uuid_raises_abort():
    with pytest.raises(HTTPException) as e:
        CoinHelper.delete_coin("invalid")
    assert "Invalid Coin ID: invalid. Coin ID must be a UUID (non-integer)." in str(e.value)

def test_delete_coin_nonexistent_raises_abort():
    random_uuid = str(uuid.uuid4())
    with pytest.raises(HTTPException) as e:
        CoinHelper.delete_coin(random_uuid)
    assert "Coin not found" in str(e.value)