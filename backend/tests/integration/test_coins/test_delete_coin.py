# DELETE COIN V1
def test_delete_coin_v1_removes_coin_from_database(client, coin):
    response = client.delete(f"/v1/coins/{coin.id}")

    assert response.status_code == 200
    assert response.json["message"] == "Coin has been successfully deleted!"

    get_response = client.get(f"/v1/coins/{coin.id}")
    assert get_response.status_code == 404


def test_delete_coin_v1_returns_400_if_invalid_id(client):
    response = client.delete("/v1/coins/invalid_id")

    assert response.status_code == 400
    assert response.json["description"] == (
        "Invalid Coin ID: invalid_id. Coin ID must be a UUID (non-integer)."
    )


def test_delete_v1_coin_returns_404_if_not_found(client):
    response = client.delete("/v1/coins/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json["description"] == "Coin not found."


# DELETE COIN V2
def test_delete_coin_v2_removes_coin_from_database_if_admin_user(logged_in_admin, client, coin):
    response = logged_in_admin.delete(f"/v2/coins/{coin.id}")

    assert response.status_code == 200
    assert response.json["message"] == "Coin has been successfully deleted!"

    get_response = client.get(f"/v3/coins/{coin.id}")
    assert get_response.status_code == 404


def test_delete_coin_v2_does_not_remove_coin_from_database_if_unauthenticated_user(client, coin):
    response = client.delete(f"/v2/coins/{coin.id}")

    assert response.status_code == 401

    get_response = client.get(f"/v3/coins/{coin.id}")
    assert get_response.status_code == 200


def test_delete_coin_v2_does_not_remove_coin_from_database_if_authenticated_user(logged_in_authenticated_user, client, coin):
    response = logged_in_authenticated_user.delete(f"/v2/coins/{coin.id}")

    assert response.status_code == 403

    get_response = client.get(f"/v3/coins/{coin.id}")
    assert get_response.status_code == 200