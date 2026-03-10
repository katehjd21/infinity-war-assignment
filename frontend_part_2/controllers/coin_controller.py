from models.coin import Coin

class CoinController:

    @staticmethod
    def fetch_all_coins():
        return Coin.fetch_coins_from_backend()


    @staticmethod
    def fetch_coin_by_id(coin_id):
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