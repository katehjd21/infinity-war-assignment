from models.coin import Coin    

class CoinController():
    @staticmethod
    def fetch_all_coins():
        return Coin.fetch_coins_from_backend()
    
    @staticmethod
    def fetch_coin_by_id(coin_id):
        return Coin.fetch_coin_from_backend_by_id(coin_id)