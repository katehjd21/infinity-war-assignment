from flask import Flask, render_template, request, session, redirect, flash, url_for
from datetime import timedelta
from controllers.duty_controller import DutyController
from controllers.coin_controller import CoinController
from utils.helpers import login_api_session, load_fixture, is_valid_password, is_valid_username
from api_session import api_session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models.coin import Coin
from decorators import login_required, admin_required
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)
app.config["SESSION_PERMANENT"] = True

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
TESTING = os.getenv("TESTING") == "1"

if TESTING:
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
    limiter = DummyLimiter()
else:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )


@app.before_request
def handle_session_persistence():
    session.permanent = True


@app.route("/test-login")
def test_login():
    if not TESTING:
        return "Not allowed", 403

    role = request.args.get("role", "user")
    session["username"] = "testuser"
    session["role"] = role
    return "Logged in for testing"


@app.route('/')
def landing_page():
    testing_mode = request.args.get("testing") == "1"
    if testing_mode:
        fixture_file = request.args.get("fixture", "coins.json")
        coins_data = load_fixture(fixture_file)
        coins = [Coin(c["name"], c["id"], c.get("duties", [])) for c in coins_data]
    else:
        try:
            coins = CoinController.fetch_all_coins()
        except Exception:
            flash("Could not load coins from backend.", "error")
            coins = []

    return render_template("coins_landing_page.html", coins=coins)


@app.route('/coin/<coin_id>')
def coin_page(coin_id):
    testing_mode = request.args.get("testing") == "1"
    if testing_mode:
        coins_data = load_fixture('coins.json')
        coin_dict = next((c for c in coins_data if c["id"] == coin_id), None)
        coin = Coin(coin_dict["name"], coin_dict["id"], coin_dict.get("duties", [])) if coin_dict else None
    else:
        coin = CoinController.fetch_coin_by_id(coin_id)
    if not coin:
        return "Coin not found", 404
    return render_template("single_coin.html", coin=coin)


@app.route("/toggle_coin_complete", methods=["POST"])
@login_required()
def toggle_coin_complete():
    coin_id = request.form.get("coin_id")
    result = CoinController.toggle_coin_complete(coin_id)

    if result is None:
        return "Server error", 500
    return redirect(request.referrer or "/")


@app.route("/duties/<duty_code>")
def duty_page(duty_code):
    coin_id = request.args.get("coin_id")
    testing_mode = request.args.get("testing") == "1"
    if testing_mode:
        duty_data = load_fixture('duties.json')
        duty_dict = next((d for d in duty_data if d["code"] == duty_code), None)
        if duty_dict:
            duty = duty_dict
            duty["coins"] = [Coin(c["name"], c["id"]) for c in duty.get("coins", [])]
        else:
            duty = None
    else:
        duty = DutyController.fetch_duty(duty_code)
    if not duty:
        return "Duty not found", 404
    return render_template("duty_detail.html", duty=duty, coin_id=coin_id)


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login_page():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not is_valid_username(username) or not is_valid_password(password):
            flash("Invalid username or password format.", "error")
            return redirect(url_for("login_page"))

        try:
            data = login_api_session(username, password)

            if not data:
                return render_template("login.html", error="Invalid credentials")

            session["role"] = data.get("role")
            session["username"] = username

            flash("Logged in successfully.", "success")
            return redirect("/")

        except requests.RequestException:
            return render_template("login.html", error="Server error. Try again later.")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    api_session.post(f"{BACKEND_URL}/logout")
    session.clear()
    flash("You have been logged out.", "success")
    return redirect("/")


@app.route("/admin/coins")
@admin_required
def admin_coins_page():
    coins = CoinController.fetch_all_coins()
    return render_template("admin_coins.html", coins=coins)


@app.route("/admin/coins/create", methods=["GET", "POST"])
@admin_required
def admin_create_coin():
    if request.method == "POST":
        name = request.form.get("name")
        duty_codes_str = request.form.get("duty_codes", "")
        duty_codes = [d.strip() for d in duty_codes_str.split(",") if d.strip()]

        completed = request.form.get("completed") == "on"

        coin, error = CoinController.create_coin(name, duty_codes=duty_codes, completed=completed)
        if coin:
            flash("Coin created successfully.", "success")
            return redirect("/admin/coins")

        return render_template(
            "admin_coin_form.html",
            coin={"name": name, "duties": [{"code": d} for d in duty_codes]},
            error=error
        )
    return render_template("admin_coin_form.html", coin=None)



@app.route("/admin/coins/<coin_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_coin(coin_id):
    coin = CoinController.fetch_coin_by_id(coin_id)
    if not coin:
        return "Coin not found", 404

    if request.method == "POST":
        name = request.form.get("name")
        duty_codes = [d.strip() for d in request.form.get("duty_codes", "").split(",") if d.strip()]
        completed = request.form.get("completed") == "on"

        updated_coin, error = CoinController.update_coin(coin_id, name=name, duty_codes=duty_codes, completed=completed)
        if updated_coin:
            flash("Coin updated successfully.", "success")
            return redirect("/admin/coins")

        return render_template(
            "admin_coin_form.html",
            coin={"id": coin_id, "name": name, "duties": [{"code": d} for d in duty_codes]},
            error=error
        )

    return render_template("admin_coin_form.html", coin=coin)



@app.route("/admin/coins/<coin_id>/delete", methods=["POST"])
@admin_required
def admin_delete_coin(coin_id):
    success = CoinController.delete_coin(coin_id)
    if success:
        flash("Coin deleted successfully.", "success")
        return redirect("/admin/coins")
    return "Failed to delete coin", 500


@app.route("/admin/duties")
@admin_required
def admin_duties_page():
    duties = DutyController.fetch_all_duties()
    return render_template("admin_duties.html", duties=duties)


@app.route("/admin/duties/create", methods=["GET", "POST"])
@admin_required
def admin_create_duty():
    all_coins = CoinController.fetch_all_coins()
    if request.method == "POST":
        code = request.form.get("code")
        name = request.form.get("name")
        description = request.form.get("description")
        coin_ids = request.form.getlist("coin_ids")
        ksb_codes = [k.strip() for k in request.form.get("ksb_codes", "").split(",") if k.strip()]
        duty, error = DutyController.create_duty(code, name, description, coin_ids=coin_ids, ksb_codes=ksb_codes)
        if duty:
            flash("Duty created successfully.", "success")
            return redirect("/admin/duties")
        return render_template(
            "admin_duty_form.html",
            duty={"code": code, "name": name, "description": description, "coins": [{"id": c} for c in coin_ids], "ksbs": ksb_codes},
            all_coins=all_coins,
            error=error
        )
    return render_template("admin_duty_form.html", all_coins=all_coins, duty=None)


@app.route("/admin/duties/<duty_code>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_duty(duty_code):
    duty = DutyController.fetch_duty(duty_code)
    if not duty:
        return "Duty not found", 404

    all_coins = CoinController.fetch_all_coins()
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        coin_ids = request.form.getlist("coin_ids")
        ksb_codes = [k.strip() for k in request.form.get("ksb_codes", "").split(",") if k.strip()]
        updated_duty, error = DutyController.update_duty(duty_code, name=name, description=description, coin_ids=coin_ids, ksb_codes=ksb_codes)
        if updated_duty:
            flash("Duty updated successfully.", "success")
            return redirect("/admin/duties")
        return render_template(
            "admin_duty_form.html",
            duty={"code": duty_code, "name": name, "description": description, "coins": [{"id": c} for c in coin_ids], "ksbs": ksb_codes},
            all_coins=all_coins,
            error=error
        )

    return render_template("admin_duty_form.html", duty=duty, all_coins=all_coins)


@app.route("/admin/duties/<duty_code>/delete", methods=["POST"])
@admin_required
def admin_delete_duty(duty_code):
    success = DutyController.delete_duty(duty_code)
    if success:
        flash("Duty deleted successfully.", "success")
        return redirect("/admin/duties")
    return "Failed to delete duty", 500


@app.route("/admin/logs")
@admin_required
def admin_logs_page():
    logs = []
    try:
        response = api_session.get(f"{BACKEND_URL}/admin/logs")
        response.raise_for_status()
        logs = response.json()
    except requests.exceptions.RequestException:
        flash("Could not load logs from backend.", "error")

    return render_template("admin_logs.html", logs=logs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)