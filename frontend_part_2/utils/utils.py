import os
import json
from api_session import api_session
import requests

def load_fixture(filename, folder="cypress/fixtures"):

    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    path = os.path.join(app_root, folder, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Fixture not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def login_api_session(username, password):
    try:
        resp = api_session.post(
            "http://localhost:5000/login",
            json={"username": username, "password": password},
            timeout=5
        )
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        print("API session login failed:", e)
        return False