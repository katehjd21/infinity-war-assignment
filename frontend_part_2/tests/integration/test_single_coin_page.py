def test_single_coin_page_get(mocker, client, mocked_coins):
    mocked_coin = mocked_coins[0]

    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    response = client.get(f'/coin/{mocked_coin.id}')
    html = response.data.decode()

    assert response.status_code == 200
    assert mocked_coin.name in html

    for duty in mocked_coin.duties:
        assert duty["code"] in html
        assert duty["name"] in html
            

def test_single_coin_page_not_found(mocker, client):
    mocker.patch("controllers.coin_controller.CoinController.fetch_coin_by_id", return_value=None)
    response = client.get('/coin/non-existent-id')

    assert response.status_code == 404