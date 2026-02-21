def test_landing_page_get(mocker, client, mocked_coins):
    mocker.patch("controllers.coin_controller.CoinController.fetch_all_coins", return_value=mocked_coins)
    response = client.get('/')
    html = response.data.decode()

    assert response.status_code == 200
    for coin in mocked_coins:
        assert coin.name in html

    for coin in mocked_coins:
        expected_href = f'href="/coin/{coin.id}"'
        assert expected_href in html