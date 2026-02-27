from models import Duty, Knowledge, Skill, Behaviour, DutyCoin, DutyKnowledge, DutySkill, DutyBehaviour


# PATCH DUTY
def test_patch_duty_updates_code(client, duty_with_coins):
    response = client.patch(f"/duties/{duty_with_coins.code}", json={
        "code": "D999"
    })

    assert response.status_code == 200
    assert response.json["code"] == "D999"


def test_patch_duty_updates_name(client, duty_with_coins):
    response = client.patch(f"/duties/{duty_with_coins.code}", json={
        "name": "Updated Duty Name"
    })

    data = response.json

    assert response.status_code == 200
    assert data["name"] == "Updated Duty Name"


def test_patch_duty_updates_description(client, duty_with_coins):
    response = client.patch(f"/duties/{duty_with_coins.code}", json={
        "description": "Updated Duty Description"
    })

    assert response.status_code == 200
    assert response.json["description"] == "Updated Duty Description"


def test_patch_duty_updates_coins(client, duty_with_coins, coins):
    new_coin_ids = [coin.id for coin in coins]

    response = client.patch(f"/duties/{duty_with_coins.code}", json={
        "coin_ids": new_coin_ids
    })

    assert response.status_code == 200

    duty = Duty.get(Duty.code == duty_with_coins.code)

    for coin in coins:
        assert DutyCoin.select().where(
            DutyCoin.duty == duty,
            DutyCoin.coin == coin
        ).exists()


def test_patch_duty_replaces_existing_coins(client, duty_with_coins, coins):
    original_duty = duty_with_coins

    new_coin_ids = [coins[0].id]

    response = client.patch(f"/duties/{original_duty.code}", json={
        "coin_ids": new_coin_ids
    })

    assert response.status_code == 200

    duty = Duty.get(Duty.code == original_duty.code)

    assert DutyCoin.select().where(DutyCoin.duty == duty).count() == 1


def test_patch_duty_updates_ksbs(client, duty_with_ksb, ksbs):
    duty, knowledge, skill, behaviour = duty_with_ksb
    new_ksb_codes = [ksbs[0].code]

    response = client.patch(f"/duties/{duty.code}", json={
        "ksb_codes": new_ksb_codes
    })

    assert response.status_code == 200

    duty = Duty.get(Duty.code == duty.code)

    total_ksbs = (
        DutyKnowledge.select().where(DutyKnowledge.duty == duty).count()
        + DutySkill.select().where(DutySkill.duty == duty).count()
        + DutyBehaviour.select().where(DutyBehaviour.duty == duty).count()
    )

    assert total_ksbs == 1

    ksb = ksbs[0]

    if isinstance(ksb, Knowledge):
        assert DutyKnowledge.select().where(
            DutyKnowledge.duty == duty,
            DutyKnowledge.knowledge == ksb
        ).exists()
    elif isinstance(ksb, Skill):
        assert DutySkill.select().where(
            DutySkill.duty == duty,
            DutySkill.skill == ksb
        ).exists()
    elif isinstance(ksb, Behaviour):
        assert DutyBehaviour.select().where(
            DutyBehaviour.duty == duty,
            DutyBehaviour.behaviour == ksb
        ).exists()


def test_patch_duty_returns_404_if_not_found(client):
    response = client.patch("/duties/D999", json={
        "name": "New Duty Name"
    })

    assert response.status_code == 404
    assert response.json["description"] == "Duty not found."


def test_patch_duty_returns_400_if_invalid_format(client):
    response = client.patch("/duties/INVALID", json={
        "name": "New Name"
    })

    assert response.status_code == 400
    assert "Invalid Duty Code format" in response.json["description"]