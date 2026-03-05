from models.coin import Coin

class CoinController:
    @staticmethod
    def fetch_all_coins():
        try:
            return Coin.fetch_coins_from_backend()
        except Exception as e:
            print("Error fetching coins:", e)
            return []

    @staticmethod
    def fetch_coin_by_id(coin_id):
        try:
            return Coin.fetch_coin_from_backend_by_id(coin_id)
        except Exception as e:
            print(f"Error fetching coin {coin_id}:", e)
            return None