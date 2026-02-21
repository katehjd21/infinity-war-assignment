import pytest
from app import app
from models.coin import Coin
from controllers.coin_controller import CoinController

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mocked_coins():
    return [
        Coin("Automate", "11111111-1111-1111-1111-111111111111"),
        Coin("Houston", "22222222-2222-2222-2222-222222222222"),
        Coin("Security", "33333333-3333-3333-3333-333333333333"),
        Coin("GoingDeeper", "44444444-4444-4444-4444-444444444444"),
        Coin("Assemble", "55555555-5555-5555-5555-555555555555"),
    ]