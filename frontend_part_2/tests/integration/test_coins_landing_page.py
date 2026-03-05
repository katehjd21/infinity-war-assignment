import pytest

def test_landing_page_shows_all_coins(mocker, client, mocked_coins):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=mocked_coins
    )

    response = client.get('/')
    html = response.data.decode()

    assert response.status_code == 200

    for coin in mocked_coins:
        assert coin.name in html

    for coin in mocked_coins:
        expected_href = f'/coin/{coin.id}'
        assert f'href="{expected_href}"' in html


def test_landing_page_with_no_coins(mocker, client):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=[]
    )

    response = client.get('/')
    html = response.data.decode()

    assert response.status_code == 200
    assert "No Coins Available" in html
    assert "grid" not in html