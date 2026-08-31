from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user, login_required
from shared.database_file.oltp_models import *
from shared.database_file.extensions import limiter

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if request.method == "POST":
        userlogin = request.form["email"]
        password = request.form["password"]

        user = Pilot.query.filter_by(pilot_email=userlogin).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("analytics.index"))

        flash("Invalid username or password")
        return redirect(url_for("login_bp.login"))

    return render_template("login.html")


@login_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("login_bp.login"))