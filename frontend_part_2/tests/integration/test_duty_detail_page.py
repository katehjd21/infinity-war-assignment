def test_duty_detail_page_get(mocker, client, mocked_duty):
    mocker.patch("controllers.duty_controller.DutyController.fetch_duty", return_value=mocked_duty)

    response = client.get(f'/duties/{mocked_duty.code}')
    html = response.data.decode()

    assert response.status_code == 200
    assert mocked_duty.code in html
    assert mocked_duty.name in html
    assert mocked_duty.description in html

    for coin in mocked_duty.coins:
        assert coin["name"] in html


def test_duty_detail_page_not_found(mocker, client):
    mocker.patch("controllers.duty_controller.DutyController.fetch_duty", return_value=None)

    response = client.get('/duties/non-existent-code')

    assert response.status_code == 404


def test_duty_detail_page_shows_back_to_coin_link(mocker, client, mocked_duty):
    mocker.patch("controllers.duty_controller.DutyController.fetch_duty", return_value=mocked_duty)

    coin_id = "11111111-1111-1111-1111-111111111111"
    response = client.get(f"/duties/{mocked_duty.code}?coin_id={coin_id}")
    html = response.data.decode()

    assert response.status_code == 200

    assert f'href="/coin/{coin_id}"' in html
    assert "Back to coin" in html

    assert 'href="/"' in html
    assert "Back to all coins" in html


def test_duty_detail_page_no_coin_link_if_not_passed(mocker, client, mocked_duty):
    mocker.patch("controllers.duty_controller.DutyController.fetch_duty", return_value=mocked_duty)

    response = client.get(f"/duties/{mocked_duty.code}")
    html = response.data.decode()

    assert response.status_code == 200
    assert "Back to coin" not in html
    assert 'href="/"' in html  