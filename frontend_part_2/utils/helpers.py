import os
import json
from api_session import api_session
import requests
import re

BACKEND_URL = os.environ.get("BACKEND_URL", "localhost:5000")

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
            f"{BACKEND_URL}/login",
            json={"username": username, "password": password},
            timeout=5
        )

        if resp.status_code != 200:
            return None

        return resp.json()

    except requests.RequestException as e:
        print("API session login failed:", e)
        return None


def is_valid_username(username):
    return bool(re.match(r"^[a-zA-Z0-9_]{3,20}$", username))


def is_valid_password(password):
    return len(password) >= 6
