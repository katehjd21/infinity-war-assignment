import pytest
from app import app
from models.coin import Coin
from controllers.coin_controller import CoinController

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

import pytest
from models.coin import Coin

@pytest.fixture
def mocked_coins():
    return [
        Coin(
            "Automate",
            "11111111-1111-1111-1111-111111111111",
            duties=[
                {"code": "D1", "name": "Duty 1", "description": "Duty 1 Description"},
                {"code": "D2", "name": "Duty 2", "description": "Duty 2 Description"},
            ]
        ),
        Coin(
            "Houston",
            "22222222-2222-2222-2222-222222222222",
            duties=[
                {"code": "D3", "name": "Duty 3", "description": "Duty 3 Description"},
            ]
        ),
        Coin(
            "Security",
            "33333333-3333-3333-3333-333333333333",
            duties=[]
        ),
        Coin(
            "GoingDeeper",
            "44444444-4444-4444-4444-444444444444",
            duties=[]
        ),
        Coin(
            "Assemble",
            "55555555-5555-5555-5555-555555555555",
            duties=[]
        ),
    ]