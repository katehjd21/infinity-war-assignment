def test_single_coin_page_get(mocker, client, mocked_coins):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coins[0]
    )
    response = client.get(f'/coin/{mocked_coins[0].id}')
    html = response.data.decode()

    assert response.status_code == 200
    assert mocked_coins[0].name in html

def test_single_coin_page_not_found(mocker, client):
    mocker.patch("controllers.coin_controller.CoinController.fetch_coin_by_id", return_value=None)
    response = client.get('/coin/non-existent-id')

    assert response.status_code == 404