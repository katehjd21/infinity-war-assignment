import pytest
from app import app
from models.coin import Coin
from models.duty import Duty

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mocked_coin():
    coin = Coin(
            "Automate",
            "11111111-1111-1111-1111-111111111111",
            duties=[
                {"code": "D1", "name": "Duty 1", "description": "Duty 1 Description"},
                {"code": "D2", "name": "Duty 2", "description": "Duty 2 Description"},
            ],
            completed=True
        )
    return coin


@pytest.fixture
def mocked_coins():
    return [
        Coin(
            "Automate",
            "11111111-1111-1111-1111-111111111111",
            duties=[
                {"code": "D1", "name": "Duty 1", "description": "Duty 1 Description"},
                {"code": "D2", "name": "Duty 2", "description": "Duty 2 Description"},
            ],
            completed=True
        ),
        Coin(
            "Houston",
            "22222222-2222-2222-2222-222222222222",
            duties=[
                {"code": "D3", "name": "Duty 3", "description": "Duty 3 Description"},
            ],
            completed=False
        ),
        Coin(
            "Security",
            "33333333-3333-3333-3333-333333333333",
            duties=[],
            completed=False
        ),
        Coin(
            "GoingDeeper",
            "44444444-4444-4444-4444-444444444444",
            duties=[],
            completed=True
            
        ),
        Coin(
            "Assemble",
            "55555555-5555-5555-5555-555555555555",
            duties=[],
            completed=False
        ),
    ]

@pytest.fixture
def mocked_coins_response():
    return [
        {
            "name": "Automate",
            "id": "11111111-1111-1111-1111-111111111111",
            "duties": [
                {"code": "D1", "name": "Duty 1", "description": "Duty 1 Description"},
                {"code": "D2", "name": "Duty 2", "description": "Duty 2 Description"},
            ],
            "completed": True
        },
        {
            "name": "Houston",
            "id": "22222222-2222-2222-2222-222222222222",
            "duties": [
                {"code": "D3", "name": "Duty 3", "description": "Duty 3 Description"},
            ],
            "completed": False
        },
        {
            "name": "Security",
            "id": "33333333-3333-3333-3333-333333333333",
            "duties": [
                {"code": "D4", "name": "Duty 4", "description": "Duty 4 Description"},
                {"code": "D5", "name": "Duty 5", "description": "Duty 5 Description"},
            ],
            "completed": False
        },
        {
            "name": "GoingDeeper",
            "id": "44444444-4444-4444-4444-444444444444",
            "duties": [],
            "completed": True
        },
        {
            "name": "Assemble",
            "id": "55555555-5555-5555-5555-555555555555",
            "completed": False
        },
    ]

@pytest.fixture
def mocked_duty():
    return Duty(
        code="D1",
        name="Duty 1",
        description="Duty 1 Description",
        coins=[
            {"name": "Automate"},
            {"name": "Houston"}
        ]
    )

@pytest.fixture
def mocked_duty_response():
    duty_response = {"code": "D1", "name": "Duty 1", "description": "Duty 1 Description", "coins": [{"name": "Automate"}]}
    return duty_response


@pytest.fixture
def logged_in_authenticated_user(client):
    with client.session_transaction() as session:
        session["username"] = "test_authenticated_user"
        session["role"] = "authenticated"
    return client


@pytest.fixture
def logged_in_admin_user(client):
    with client.session_transaction() as session:
        session["username"] = "test_admin_user"
        session["role"] = "admin"
    return client