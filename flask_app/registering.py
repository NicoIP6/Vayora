from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from shared.database_file.oltp_models import *
from email_validator import validate_email, EmailNotValidError

registering_bp = Blueprint("registering_bp", __name__)

@registering_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        lastname = request.form.get("lastname")

        try:
            validate_email(email, check_deliverability=False).normalized
        except EmailNotValidError:
            flash("This email is already registered")
            return redirect(url_for(".register"))

        try:
            pilotnumber = int(request.form.get("pilotnumber", "").strip())
        except ValueError:
            flash("Pilot number must be an integer", "error")
            return redirect(url_for(".register"))

        if not all([email, password, pilotnumber, name, lastname]):
            flash("All fields are required")
            return redirect(url_for(".register"))

        if Pilot.query.filter_by(pilot_number=pilotnumber).first():
            flash("This pilot number is already registered")
            return redirect(url_for(".register"))


        user = Pilot(
            pilot_email=email,
            pilot_firstname=name,
            pilot_lastname=lastname,
            pilot_number=pilotnumber
            )

        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("You have been successfully registered")
        return redirect(url_for("login_bp.login"))

    return render_template("register.html", show_popup=False)
