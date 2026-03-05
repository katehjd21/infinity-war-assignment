import os
import json
from utils.utils import load_fixture

def test_load_fixture_returns_data():
    fixture_name = "test_utils.json"

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    fixtures_dir = os.path.join(project_root, "utils", "fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)

    fixture_path = os.path.join(fixtures_dir, fixture_name)

    sample_data = [{"id": "uuid-1", "name": "Test Coin"}]

    with open(fixture_path, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)

    try:
        result = load_fixture(fixture_name, folder="utils/fixtures")
        assert result == sample_data
    finally:
        os.remove(fixture_path)

    try:
        os.rmdir(fixtures_dir)
    except OSError:
        pass