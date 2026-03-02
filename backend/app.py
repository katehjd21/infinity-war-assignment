from flask import Flask, jsonify, request, session
import secrets
from models import Coin, User, RequestLog
from helpers.duty import DutyHelper
from helpers.coin import CoinHelper
from helpers.ksb import KsbHelper
from utils.helper_functions import serialize_coin, serialize_coin_with_duties, serialize_duty_with_coins_and_ksbs
from decorators import admin_required, login_required
from pg_db_connection import pg_db, database 
import os

database.initialize(pg_db)
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.before_request
def before_request():
    if os.getenv("TESTING"):
        return
    if pg_db.is_closed(): 
        pg_db.connect(reuse_if_open=True)

@app.before_request
def log_request():
    if request.endpoint == "static":
        return

    user = None
    if "user_id" in session:
        user = User.get_or_none(User.id == session["user_id"])

    RequestLog.create(
        method=request.method,
        path=request.path,
        user=user
    )

@app.teardown_request
def teardown_request(exception):
    if not os.getenv("TESTING") and not pg_db.is_closed():
        pg_db.close()

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"description": error.description}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"description": error.description}), 404


# GET COINS
@app.get("/v1/coins")
def get_coins_v1():
    coins = Coin.select()
    return jsonify([serialize_coin(coin) for coin in coins]), 200

@app.get("/v2/coins")
def get_coins_v2():
    coins = Coin.select()
    return jsonify([serialize_coin_with_duties(coin) for coin in coins]), 200

@app.get("/v3/coins")
def get_coins_v3():
    coins = Coin.select()
    return jsonify([serialize_coin_with_duties(coin, include_completed=True) for coin in coins]), 200

# GET COIN BY ID
@app.get("/v1/coins/<coin_id>")
def get_coin_by_id_v1(coin_id):
    coin = CoinHelper.get_coin_by_id(coin_id)
    return jsonify(serialize_coin(coin)), 200

@app.get("/v2/coins/<coin_id>")
def get_coin_by_id_v2(coin_id):
    coin = CoinHelper.get_coin_by_id(coin_id)
    return jsonify(serialize_coin_with_duties(coin)), 200

@app.get("/v3/coins/<coin_id>")
def get_coin_by_id_v3(coin_id):
    coin = CoinHelper.get_coin_by_id(coin_id)
    return jsonify(serialize_coin_with_duties(coin, include_completed=True)), 200


# POST/CREATE COIN
@app.post("/v1/coins")
def create_coin_v1():
    coin = CoinHelper.create_coin(request.json, with_duties=False)
    return jsonify(serialize_coin(coin)), 201

@app.post("/v2/coins")
def create_coin_v2():
    coin = CoinHelper.create_coin(request.json, with_duties=True)
    return jsonify(serialize_coin_with_duties(coin)), 201

@app.post("/v3/coins")
@admin_required
def create_coin_v3():
    coin = CoinHelper.create_coin(request.json, with_duties=True)
    return jsonify(serialize_coin_with_duties(coin, include_completed=True)), 201


# POST (TOGGLE) COMPLETED COIN
@app.post("/coins/<coin_id>/complete")
@login_required
def complete_coin(coin_id):
    new_state = CoinHelper.toggle_complete_coin(coin_id)
    return jsonify({"message": "Coin completion toggled", "completed": new_state}), 200


# PATCH/UPDATE COIN
@app.patch("/v1/coins/<coin_id>")
def update_coin_v1(coin_id):
    coin = CoinHelper.update_coin(coin_id, request.json, require_name=True)
    return jsonify(serialize_coin(coin)), 200

@app.patch("/v2/coins/<coin_id>")
def update_coin_v2(coin_id):
    coin = CoinHelper.update_coin(coin_id, request.json, require_name=False)
    return jsonify(serialize_coin_with_duties(coin)), 200

@app.patch("/v3/coins/<coin_id>")
@admin_required
def update_coin_v3(coin_id):
    coin = CoinHelper.update_coin(coin_id, request.json, require_name=False)
    return jsonify(serialize_coin_with_duties(coin, include_completed=True)), 200

# DELETE COIN
@app.delete("/v1/coins/<coin_id>")
def delete_coin_v1(coin_id):
    CoinHelper.delete_coin(coin_id)
    return jsonify({"message": "Coin has been successfully deleted!"}), 200

@app.delete("/v2/coins/<coin_id>")
@admin_required
def delete_coin_v2(coin_id):
    CoinHelper.delete_coin(coin_id)
    return jsonify({"message": "Coin has been successfully deleted!"}), 200


# GET DUTIES
@app.get("/duties")
def get_duties():
    return jsonify(DutyHelper.list_all_duties()), 200


# GET DUTY BY CODE WITH ASSOCIATED COINS
@app.get("/duties/<duty_code>")
def get_duty_by_code(duty_code):
    return jsonify(DutyHelper.get_duty_by_code(duty_code)), 200


# POST DUTY
@app.post("/v1/duties")
def create_duty_v1():
    duty = DutyHelper.create_duty(request.json)
    return jsonify(serialize_duty_with_coins_and_ksbs(duty)), 201

@app.post("/v2/duties")
@admin_required
def create_duty_v2():
    duty = DutyHelper.create_duty(request.json)
    return jsonify(serialize_duty_with_coins_and_ksbs(duty)), 201
    


# PATCH/UPDATE DUTY
@app.patch("/v1/duties/<duty_code>")
def update_duty_v1(duty_code):
    duty = DutyHelper.update_duty(duty_code, request.json)
    return jsonify(serialize_duty_with_coins_and_ksbs(duty)), 200

@app.patch("/v2/duties/<duty_code>")
@admin_required
def update_duty_v2(duty_code):
    duty = DutyHelper.update_duty(duty_code, request.json)
    return jsonify(serialize_duty_with_coins_and_ksbs(duty)), 200


# DELETE DUTY
@app.delete("/v1/duties/<duty_code>")
def delete_duty_v1(duty_code):
    DutyHelper.delete_duty(duty_code)
    return jsonify({"message": "Duty has been successfully deleted!"}), 200

@app.delete("/v2/duties/<duty_code>")
@admin_required
def delete_duty_v2(duty_code):
    DutyHelper.delete_duty(duty_code)
    return jsonify({"message": "Duty has been successfully deleted!"}), 200


# GET KSBS
@app.get("/ksbs")
def get_ksbs():
    return jsonify(KsbHelper.list_all_ksbs()), 200


# GET KSB BY KSB CODE WITH ASSOCIATED DUTIES
@app.get("/ksbs/<ksb_code>")
def get_ksb_by_code(ksb_code):
    return jsonify(KsbHelper.get_ksb_by_code(ksb_code)), 200


# AUTHENTICATION
@app.post("/login")
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.get_or_none(User.username == username)

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = str(user.id)
    session["role"] = user.role

    return jsonify({"message": "Login successful", "role": user.role}), 200


@app.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200


@app.get("/admin/logs")
@admin_required
def view_logs():
    logs = (RequestLog
            .select()
            .order_by(RequestLog.timestamp.desc())
            .limit(100))

    return jsonify([
        {
            "method": log.method,
            "path": log.path,
            "user": log.user.username if log.user else "Anonymous",
            "timestamp": log.timestamp
        }
        for log in logs
    ])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)  