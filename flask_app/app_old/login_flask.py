from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from shared.database_file.set_up import Setup
from flask_app.statistics import analytics
from shared.database_file.oltp_models import *

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        userlogin = request.form["email"]
        password = request.form["password"]

        user = Pilot.query.filter_by(pilot_email=userlogin).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("analytics.index", pilot_number=user.pilot_number))
        else:
            flash("Invalid username or password")
            return redirect(url_for("login"))

    return render_template("login.html")


@login_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("login_bp.login"))