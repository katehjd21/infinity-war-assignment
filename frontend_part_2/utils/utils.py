import os
import json

def load_fixture(filename, folder="cypress/fixtures"):

    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    path = os.path.join(app_root, folder, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Fixture not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)