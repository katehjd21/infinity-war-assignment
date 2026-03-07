def test_admin_coins_page_shows_coins(mocker, logged_in_admin_user, mocked_coins):
    mocker.patch("controllers.coin_controller.CoinController.fetch_all_coins", return_value=mocked_coins)

    client = logged_in_admin_user
    response = client.get("/admin/coins")
    html = response.data.decode()

    assert response.status_code == 200
    for coin in mocked_coins:
        assert coin.name in html
        for duty in coin.duties:
            assert duty["code"] in html


