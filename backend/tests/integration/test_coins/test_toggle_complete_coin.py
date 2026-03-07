from models import Coin

def test_authenticated_user_can_toggle_coin_completion(logged_in_admin, coin):
    assert not coin.completed

    response = logged_in_admin.post(f"/coins/{coin.id}/complete")
    assert response.status_code == 200
    data = response.get_json()
    assert data["coin_id"] == str(coin.id)
    assert data["completed"] is True

    coin = Coin.get_by_id(coin.id)
    assert coin.completed is True

    response = logged_in_admin.post(f"/coins/{coin.id}/complete")
    assert response.status_code == 200
    coin = Coin.get_by_id(coin.id)
    assert coin.completed is False

def test_admin_can_toggle_coin_completion(logged_in_admin, coin):
    response = logged_in_admin.post(f"/coins/{coin.id}/complete")
    assert response.status_code == 200


def test_unauthenticated_user_cannot_toggle_coin_completion(client, coin):
    response = client.post(f"/coins/{coin.id}/complete")
    assert response.status_code == 401

def test_toggle_coin_returns_404_if_coin_not_found(logged_in_admin):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = logged_in_admin.post(f"/coins/{fake_id}/complete")
    assert response.status_code == 404