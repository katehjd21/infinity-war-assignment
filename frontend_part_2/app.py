from flask import Flask,render_template
from controllers.duty_controller import DutyController
from controllers.coin_controller import CoinController

app = Flask(__name__)

@app.route('/')
def landing_page():
    coins = CoinController().fetch_all_coins()
    return render_template("coins.html", coins=coins)

@app.route('/coin/<coin_id>')
def coin_page(coin_id):
    coin = CoinController.fetch_coin_by_id(coin_id)
    if not coin:
        return "Coin not found", 404
    return render_template("single_coin.html", coin=coin)

@app.route("/duties/<duty_code>")
def duty_page(duty_code):
    duty = DutyController().fetch_duty(duty_code)
    if not duty:
        return "Duty not found", 404
    return render_template("duty_detail.html", duty=duty)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
 