def test_admin_coins_page_shows_coins(mocker, logged_in_admin_user, mocked_coins):
    mocker.patch("controllers.coin_controller.CoinController.fetch_all_coins", return_value=mocked_coins)

    client = logged_in_admin_user
    response = client.get("/admin/coins")
    html = response.data.decode()

    assert response.status_code == 200
    assert "<h1>Admin - Coins</h1>" in html
    assert 'Create New Coin' in html

    for coin in mocked_coins:
        assert coin.name in html
        for duty in coin.duties:
            assert duty["code"] in html


def test_admin_coins_page_row_details(mocker, logged_in_admin_user, mocked_coins):
    mocker.patch("controllers.coin_controller.CoinController.fetch_all_coins", return_value=mocked_coins)

    client = logged_in_admin_user
    response = client.get("/admin/coins")
    html = response.data.decode()

    assert response.status_code == 200

    for coin in mocked_coins:
        assert coin.name in html

        if coin.completed:
            assert "✓ Completed" in html
        else:
            assert "⏳ In Progress" in html

        for duty in coin.duties:
            assert duty["code"] in html

        edit_href = f'/admin/coins/{coin.id}/edit'
        assert f'href="{edit_href}"' in html

        delete_form_action = f'/admin/coins/{coin.id}/delete'
        assert f'action="{delete_form_action}"' in html
        assert '<button type="submit" class="delete-button">' in html


def test_admin_coins_create_link(mocker, logged_in_admin_user, mocked_coins):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=mocked_coins
    )

    response = logged_in_admin_user.get("/admin/coins")
    html = response.data.decode()

    assert 'href="/admin/coins/create"' in html


def test_admin_coins_page_redirect_non_admin(logged_in_authenticated_user, mocker, mocked_coins):
    mocker.patch("controllers.coin_controller.CoinController.fetch_all_coins", return_value=mocked_coins)

    response = logged_in_authenticated_user.get("/admin/coins", follow_redirects=True)
    html = response.data.decode()

    assert response.status_code == 200
    assert "You do not have permission to access this page." in html
    assert "<h1>Apprenticeship Coins</h1>" in html


def test_admin_coins_page_redirect_anonymous(client):
    response = client.get("/admin/coins", follow_redirects=True)
    html = response.data.decode()

    assert response.status_code == 200
    assert "You must be logged in to access this page." in html
    assert "<h1>Login</h1>" in html


def test_admin_coins_page_with_no_coins(mocker, logged_in_admin_user):
    mocker.patch("controllers.coin_controller.CoinController.fetch_all_coins", return_value=[])

    response = logged_in_admin_user.get("/admin/coins")
    html = response.data.decode()

    assert response.status_code == 200
    assert "<tbody>" in html
    assert "Edit" not in html
    assert "Delete" not in html


def test_admin_coins_page_backend_failure(mocker, logged_in_admin_user):
    mocker.patch("controllers.coin_controller.CoinController.fetch_all_coins", side_effect=Exception("Backend down"))

    response = logged_in_admin_user.get("/admin/coins", follow_redirects=True)
    html = response.data.decode()

    assert response.status_code == 200
    assert "Your session has expired. Please log in again." in html
    assert "<h1>Login</h1>" in html


