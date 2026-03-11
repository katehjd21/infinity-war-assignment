def test_duty_detail_page_shows_duty(mocker, client, mocked_duty):
    mocker.patch("controllers.duty_controller.DutyController.fetch_duty", return_value=mocked_duty)

    response = client.get(f'/duties/{mocked_duty.code}')
    html = response.data.decode()

    assert response.status_code == 200
    assert mocked_duty.code in html
    assert mocked_duty.name in html
    assert mocked_duty.description in html


def test_duty_detail_shows_associated_coins_with_correct_links(mocker, client, mocked_duty):
    mocker.patch("controllers.duty_controller.DutyController.fetch_duty", return_value=mocked_duty)
    
    response = client.get(f"/duties/{mocked_duty.code}")
    html = response.data.decode()
    
    for coin in mocked_duty.coins:
        expected_href = f'/coin/{coin["id"]}'
        assert expected_href in html
        assert coin["name"] in html


def test_duty_detail_shows_message_if_no_coins(mocker, client, mocked_duty):
    duty_no_coins = mocked_duty
    duty_no_coins.coins = []
    mocker.patch("controllers.duty_controller.DutyController.fetch_duty", return_value=duty_no_coins)

    response = client.get(f"/duties/{duty_no_coins.code}")
    html = response.data.decode()

    assert response.status_code == 200
    assert "No coins associated with this duty." in html


def test_duty_detail_shows_ksb_codes(mocker, client, mocked_duty):
    mocker.patch("controllers.duty_controller.DutyController.fetch_duty", return_value=mocked_duty)
    
    response = client.get(f"/duties/{mocked_duty.code}")
    html = response.data.decode()
    
    for ksb in mocked_duty.ksbs:
        assert ksb in html


def test_duty_detail_shows_message_if_no_ksbs(mocker, client, mocked_duty):
    duty_no_ksbs = mocked_duty
    duty_no_ksbs.ksbs = []
    mocker.patch("controllers.duty_controller.DutyController.fetch_duty", return_value=duty_no_ksbs)
    
    response = client.get(f"/duties/{duty_no_ksbs.code}")
    html = response.data.decode()
    
    assert "No KSB codes for this duty." in html


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