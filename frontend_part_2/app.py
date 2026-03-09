from flask import Flask, render_template, request, session, redirect, flash, url_for
from controllers.duty_controller import DutyController
from controllers.coin_controller import CoinController
from utils.utils import login_api_session, load_fixture
from api_session import api_session
from models.coin import Coin
from decorators import login_required, admin_required
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


@app.route('/')
def landing_page():
    testing_mode = request.args.get("testing") == "1"
    if testing_mode:
        fixture_file = request.args.get("fixture", "coins.json")
        coins_data = load_fixture(fixture_file)
        coins = [Coin(c["name"], c["id"], c.get("duties", [])) for c in coins_data]
    else:
        coins = CoinController.fetch_all_coins()
    return render_template("coins.html", coins=coins)


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
    try:
        result = CoinController.toggle_coin_complete(coin_id)
    except Exception:
        session.clear()
        flash("Your session has expired. Please log in again.", "error")
        return redirect(url_for("login_page"))

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


@app.route("/api/session_status")
def session_status():
    return {"logged_in": bool(session.get("username"))}


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

            if not login_api_session(username, password):
                return render_template("login.html", error="API session login failed. Try again.")

            flash("Logged in successfully.", "success")
            return redirect("/")
        except requests.RequestException:
            return render_template("login.html", error="Server error. Try again later.")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    api_session.post("http://localhost:5000/logout")
    session.clear()
    flash("You have been logged out.", "success")
    return redirect("/")


@app.route("/admin/coins")
@admin_required
def admin_coins_page():
    try:
        coins = CoinController.fetch_all_coins()
        return render_template("admin_coins.html", coins=coins)
    except Exception:
        session.clear()
        flash("Your session has expired. Please log in again.", "error")
        return redirect(url_for("login_page"))


@app.route("/admin/coins/create", methods=["GET", "POST"])
@admin_required
def admin_create_coin():
    try:
        if request.method == "POST":
            name = request.form.get("name")
            duty_codes_str = request.form.get("duty_codes", "")
            duty_codes = [d.strip() for d in duty_codes_str.split(",") if d.strip()]

            coin, error = CoinController.create_coin(name, duty_codes=duty_codes)
            if coin:
                flash("Coin created successfully.", "success")
                return redirect("/admin/coins")
            
            return render_template(
                "admin_coin_form.html",
                coin={"name": name, "duties": [{"code": d} for d in duty_codes]},
                error=error
            )
        return render_template("admin_coin_form.html", coin=None)
    except Exception:
        session.clear()
        flash("Your session has expired. Please log in again.", "error")
        return redirect(url_for("login_page"))


@app.route("/admin/coins/<coin_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_coin(coin_id):
    try:
        coin = CoinController.fetch_coin_by_id(coin_id)
        if not coin:
            return "Coin not found", 404
        if request.method == "POST":
            name = request.form.get("name")
            duty_codes = [d.strip() for d in request.form.get("duty_codes", "").split(",") if d.strip()]
            updated_coin, error = CoinController.update_coin(coin_id, name=name, duty_codes=duty_codes)
            if updated_coin:
                flash("Coin updated successfully.", "success")
                return redirect("/admin/coins")
            return render_template(
                "admin_coin_form.html",
                coin={"id": coin_id, "name": name, "duties": [{"code": d} for d in duty_codes]},
                error=error
            )
        return render_template("admin_coin_form.html", coin=coin)
    except Exception:
        session.clear()
        flash("Your session has expired. Please log in again.", "error")
        return redirect(url_for("login_page"))


@app.route("/admin/coins/<coin_id>/delete", methods=["POST"])
@admin_required
def admin_delete_coin(coin_id):
    try:
        success = CoinController.delete_coin(coin_id)
        if success:
            flash("Coin deleted successfully.", "success")
            return redirect("/admin/coins")
        return "Failed to delete coin", 500
    except Exception:
        session.clear()
        flash("Your session has expired. Please log in again.", "error")
        return redirect(url_for("login_page"))


@app.route("/admin/duties")
@admin_required
def admin_duties_page():
    try:
        duties = DutyController.fetch_all_duties()
        return render_template("admin_duties.html", duties=duties)
    except Exception:
        session.clear()
        flash("Your session has expired. Please log in again.", "error")
        return redirect(url_for("login_page"))


@app.route("/admin/duties/create", methods=["GET", "POST"])
@admin_required
def admin_create_duty():
    try:
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
    except Exception:
        session.clear()
        flash("Your session has expired. Please log in again.", "error")
        return redirect(url_for("login_page"))


@app.route("/admin/duties/<duty_code>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_duty(duty_code):
    try:
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
    except Exception:
        session.clear()
        flash("Your session has expired. Please log in again.", "error")
        return redirect(url_for("login_page"))


@app.route("/admin/duties/<duty_code>/delete", methods=["POST"])
@admin_required
def admin_delete_duty(duty_code):
    try:
        success = DutyController.delete_duty(duty_code)
        if success:
            flash("Duty deleted successfully.", "success")
            return redirect("/admin/duties")
        return "Failed to delete duty", 500
    except Exception:
        session.clear()
        flash("Your session has expired. Please log in again.", "error")
        return redirect(url_for("login_page"))


@app.route("/admin/logs")
@admin_required
def admin_logs_page():
    try:
        response = api_session.get("http://localhost:5000/admin/logs")
        response.raise_for_status()

        logs = response.json()

        return render_template("admin_logs.html", logs=logs)

    except requests.exceptions.RequestException:
        session.clear()
        flash("Your session has expired. Please log in again.", "error")
        return redirect(url_for("login_page"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)