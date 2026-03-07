from models import Duty, DutyCoin, DutyKnowledge, DutySkill, DutyBehaviour

# GET DUTY BY CODE
def test_get_duty_by_code_returns_its_associated_coins(client, duties, coins_with_duties):
    for duty in duties:
        response = client.get(f"/duties/{duty.code}")
        coin_names = {coin["name"] for coin in response.json.get("coins", [])}

        expected_coins = {
            coin.name
            for coin in coins_with_duties
            if DutyCoin.select().where(DutyCoin.coin == coin, DutyCoin.duty == duty).exists()
        }

        assert coin_names == expected_coins


def test_get_duty_by_code_returns_empty_coins_when_none_associated(client):
    duty = Duty.create(code="D10", name="Duty 10", description="No Coins")
    response = client.get(f"/duties/{duty.code}")
    assert response.status_code == 200
    assert response.json["coins"] == []


def test_get_duty_by_code_returns_duty_code_name_and_description(client, duties):
    for duty in duties:
        response = client.get(f"/duties/{duty.code}")
        data = response.json

        assert data["code"] == duty.code
        assert data["name"] == duty.name
        assert data["description"] == duty.description


def test_get_duty_by_code_only_returns_expected_fields(client, duties):
    expected_fields = {"id", "code", "name", "description", "coins", "ksbs"}

    for duty in duties:
        response = client.get(f"/duties/{duty.code}")
        assert set(response.json.keys()) == expected_fields


def test_duty_coins_return_id_and_name_of_coins(client, duties, coins_with_duties):
    for duty in duties:
        response = client.get(f"/duties/{duty.code}")
        for coin in response.json.get("coins", []):
            assert set(coin.keys()) == {"id", "name"}


def test_get_duty_by_code_v2_returns_coins_and_ksbs(client, duties, coins, ksbs):
    duty = duties[0]
    from helpers.duty import DutyHelper
    DutyHelper.attach_coins_to_duty(duty, [str(coins[0].id)])
    DutyHelper.attach_ksbs_to_duty(duty, [ksbs[0].code])

    response = client.get(f"/duties/{duty.code}")
    data = response.json

    assert data["code"] == duty.code
    assert len(data["coins"]) == 1
    assert data["coins"][0]["id"] == str(coins[0].id)
    assert len(data["ksbs"]) == 1
    assert data["ksbs"][0] == ksbs[0].code


def test_get_duty_by_code_returns_400_if_invalid_code(client):
    response = client.get("/duties/invalid_code")
    assert response.status_code == 400
    assert response.json["description"] == "Invalid Duty Code format. Duty Code must start with a 'D' (case-insensitive) followed by numbers (e.g., D7 or d7)."


def test_get_duty_by_code_returns_400_if_invalid_format(client):
    invalid_codes = ["d", "D", "Dabc", "D1A", "123"]
    for code in invalid_codes:
        response = client.get(f"/duties/{code}")
        assert response.status_code == 400


def test_get_duty_by_code_returns_404_if_not_found(client):
    response = client.get("/duties/D999")
    assert response.status_code == 404
    assert response.json["description"] == "Duty not found."


def test_deleting_duty_cascades_all_ksb_junction_tables(duty_with_ksbs):
    duty = duty_with_ksbs

    duty.delete_instance(recursive=True)

    assert Duty.select().where(Duty.id == duty.id).count() == 0
    assert DutyKnowledge.select().where(DutyKnowledge.duty == duty).count() == 0
    assert DutySkill.select().where(DutySkill.duty == duty).count() == 0
    assert DutyBehaviour.select().where(DutyBehaviour.duty == duty).count() == 0