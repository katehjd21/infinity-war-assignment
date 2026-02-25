from flask import Flask, render_template, request
from controllers.duty_controller import DutyController
from controllers.coin_controller import CoinController
from models.coin import Coin
from utils.utils import load_fixture

app = Flask(__name__)


@app.route('/')
def landing_page():
    testing_mode = request.args.get("testing") == "1"

    if testing_mode:
        fixture_file = request.args.get("fixture", "coins.json")
        coins_data = load_fixture(fixture_file)
        coins = [Coin(c["name"], c["id"], c.get("duties", [])) for c in coins_data]
    else:
        coins = CoinController().fetch_all_coins()

    return render_template("coins.html", coins=coins)


@app.route('/coin/<coin_id>')
def coin_page(coin_id):
    testing_mode = request.args.get("testing") == "1"

    if testing_mode:
        coins_data = load_fixture('coins.json')
        coin_dict = next((coin for coin in coins_data if coin["id"] == coin_id), None)
        if coin_dict:
            coin = Coin(
                coin_dict["name"],
                coin_dict["id"],
                coin_dict.get("duties", [])
            )
        else:
            coin = None
    else:
        coin = CoinController.fetch_coin_by_id(coin_id)

    if not coin:
        return "Coin not found", 404

    return render_template("single_coin.html", coin=coin)


@app.route("/duties/<duty_code>")
def duty_page(duty_code):
    coin_id = request.args.get("coin_id")
    testing_mode = request.args.get("testing") == "1"

    if testing_mode:
        duty_data = load_fixture('duties.json')
        duty_dict = next((duty for duty in duty_data if duty["code"] == duty_code), None)
        if duty_dict:
            duty = duty_dict
            duty["coins"] = [Coin(coin["name"], coin["id"]) for coin in duty.get("coins", [])]
        else:
            duty = None
    else:
        duty = DutyController().fetch_duty(duty_code)

    if not duty:
        return "Duty not found", 404

    return render_template("duty_detail.html", duty=duty, coin_id=coin_id)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)