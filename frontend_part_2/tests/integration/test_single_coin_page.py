from models.coin import Coin

# def test_single_coin_page_shows_coin_name(mocker, client, mocked_coin):
#     mocker.patch(
#         "controllers.coin_controller.CoinController.fetch_coin_by_id",
#         return_value=mocked_coin
#     )

#     response = client.get(f'/coin/{mocked_coin.id}')
#     html = response.data.decode()

#     assert response.status_code == 200
#     assert mocked_coin.name in html


def test_single_coin_page_shows_coin_name(mocker, client, mocked_coin):
    # Mock the controller
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    # Unauthenticated client should still see the coin name
    response = client.get(f'/coin/{mocked_coin.id}')
    html = response.data.decode()

    assert response.status_code == 200
    assert mocked_coin.name in html


def test_single_coin_page_shows_coins_associated_duties(mocker, client, mocked_coin):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    response = client.get(f'/coin/{mocked_coin.id}')
    html = response.data.decode()

    assert response.status_code == 200

    for duty in mocked_coin.duties:
        assert duty["code"] in html
        assert duty["name"] in html


def test_single_coin_page_duty_links_are_correct(mocker, client, mocked_coin):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    response = client.get(f'/coin/{mocked_coin.id}')
    html = response.data.decode()

    for duty in mocked_coin.duties:
        expected_href = f'/duties/{duty["code"]}?coin_id={mocked_coin.id}'
        assert expected_href in html


def test_single_coin_page_handles_coin_with_no_associated_duties_with_message(mocker, client):
    coin = Coin(
        "Automate",
        "11111111-1111-1111-1111-111111111111",
        completed=False
    )
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=coin
    )

    response = client.get(f'/coin/{coin.id}')
    html = response.data.decode()

    assert response.status_code == 200
    assert "No duties associated with this coin." in html


def test_single_coin_page_shows_completed_badge(mocker, logged_in_authenticated_user, mocked_coin):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    response = logged_in_authenticated_user.get(f'/coin/{mocked_coin.id}')
    html = response.data.decode()

    assert "✓ Coin Completed" in html
    assert "Mark Incomplete" in html


def test_single_coin_page_shows_in_progress_badge(mocker, logged_in_authenticated_user, mocked_coin):
    mocked_coin.completed = False

    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    response = logged_in_authenticated_user.get(f'/coin/{mocked_coin.id}')
    html = response.data.decode()

    assert "⏳ In Progress" in html
    assert "Mark Complete" in html


def test_single_coin_page_hides_toggle_when_not_logged_in(mocker, client, mocked_coin):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    response = client.get(f'/coin/{mocked_coin.id}')
    html = response.data.decode()

    assert "Mark Complete" not in html
    assert "Mark Incomplete" not in html


def test_single_coin_page_shows_toggle_when_logged_in(mocker, logged_in_authenticated_user, mocked_coin):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    response = logged_in_authenticated_user.get(f'/coin/{mocked_coin.id}')
    html = response.data.decode()

    assert "Mark Complete" in html or "Mark Incomplete" in html
    assert 'form method="POST" action="/toggle_coin_complete"' in html


def test_single_coin_page_has_back_link(mocker, client, mocked_coin):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    response = client.get(f'/coin/{mocked_coin.id}')
    html = response.data.decode()

    assert 'href="/"' in html
    assert "Back to all coins" in html


def test_single_coin_page_not_found(mocker, client):
    mocker.patch("controllers.coin_controller.CoinController.fetch_coin_by_id", return_value=None)
    response = client.get('/coin/non-existent-id')

    assert response.status_code == 404