from flask import Flask, render_template, request, session, redirect
from controllers.duty_controller import DutyController
from controllers.coin_controller import CoinController
from api_session import api_session
from models.coin import Coin
from utils.utils import load_fixture
import requests
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


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
        coin = CoinController().fetch_coin_by_id(coin_id)

    if not coin:
        return "Coin not found", 404

    return render_template("single_coin.html", coin=coin)


@app.route("/toggle_coin_complete", methods=["POST"])
def toggle_coin_complete():
    print("Toggle route hit")

    if not session.get("username"):
        print("No session user")
        return "Unauthorized", 401

    coin_id = request.form.get("coin_id")
    print("Coin ID:", coin_id)

    try:
        response = api_session.post(f"http://localhost:5000/coins/{coin_id}/complete")
        print("Backend status:", response.status_code)
        print("Backend response:", response.text)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Error toggling:", e)
        return "Server error", 500

    return redirect(request.referrer or "/")


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


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        try:
            response = api_session.post(
                "http://localhost:5000/login",
                json={"username": username, "password": password},
                timeout=5
            )
            data = response.json()
            if response.status_code != 200:
                return render_template("login.html", error=data.get("error", "Invalid credentials"))

            session["role"] = data.get("role")
            session["username"] = username
            return redirect("/")
        except requests.RequestException:
            return render_template("login.html", error="Server error. Try again later.")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout_page():
    api_session.post("http://localhost:5000/logout")
    session.clear()
    return redirect("/")


@app.route("/admin/logs")
def admin_logs_page():
    if session.get("role") != "admin":
        return "Unauthorized", 401

    try:
        response = requests.get(
            "http://localhost:5000/admin/logs",
            timeout=5
        )
        response.raise_for_status()
        logs = response.json()
    except requests.RequestException:
        logs = []
    
    return render_template("admin_logs.html", logs=logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)