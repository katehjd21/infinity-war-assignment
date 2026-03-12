from models.coin import Coin
from utils.helpers import load_fixture

class CoinController:

    @staticmethod
    def fetch_all_coins(testing=False, fixture_file="coins.json"):
        if testing:
            coins_data = load_fixture(fixture_file)
            return [Coin(c["name"], c["id"], c.get("duties", []), c.get("completed", False)) for c in coins_data]
        return Coin.fetch_coins_from_backend()


    @staticmethod
    def fetch_coin_by_id(coin_id, testing=False):
        if testing:
            coins_data = load_fixture("coins.json")
            coin_dict = next((c for c in coins_data if c["id"] == coin_id), None)
            return Coin(
                coin_dict["name"],
                coin_dict["id"],
                coin_dict.get("duties", []),
                coin_dict.get("completed", False)
            ) if coin_dict else None
        return Coin.fetch_coin_from_backend_by_id(coin_id)
    
    
    @staticmethod
    def toggle_coin_complete(coin_id):
        return Coin.toggle_complete(coin_id)


    @staticmethod
    def create_coin(name, duty_codes=None, completed=False):
        return Coin.create_coin(name, duty_codes, completed)


    @staticmethod
    def update_coin(coin_id, name=None, duty_codes=None, completed=False):
        return Coin.update_coin(coin_id, name, duty_codes, completed)


    @staticmethod
    def delete_coin(coin_id):
        return Coin.delete_coin(coin_id)