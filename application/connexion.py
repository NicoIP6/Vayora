from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from application.set_up import Setup
from application.extensions import db, bcrypt, login_manager
from db.oltp_models import *
from db.dwh_models import *
from application.statistics import analytics


def register_routes(app):
    """
    Register routes
    :return: the HTML for registering
    """

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            update_confirm = request.form.get("update_confirm")


            # !!!!!! ----> This part is only for demonstration purposes and will be removed in an upcoming commit. <---- !!!!!!!!
            # If it's a pop up response
            if update_confirm in ["true", "false"]:
                temp_data = session.get('temp_register_data')
                if not temp_data:
                    flash("Session expired. Please try again.")
                    return redirect(url_for("register"))

                email = temp_data['email']
                password = temp_data['password']
                pilotnumber = temp_data['pilotnumber']
                name = temp_data['name']
                lastname = temp_data['lastname']

                # If canceled
                if update_confirm == "false":
                    session.pop('temp_register_data', None)
                    flash("Registration cancelled")
                    return redirect(url_for("register"))

                # If update wanted
                if update_confirm == "true":
                    existing_pilot = Pilot.query.filter_by(pilot_number=pilotnumber).first()
                    existing_pilot.pilot_email = email
                    existing_pilot.pilot_firstname = name
                    existing_pilot.pilot_lastname = lastname
                    existing_pilot.set_password(password)
                    db.session.commit()
                    session.pop('temp_register_data', None)
                    flash("Your information has been successfully updated")
                    return redirect(url_for("login"))

            # Sinon, c'est une nouvelle soumission du formulaire
            else:
                email = request.form.get("email")
                password = request.form.get("password")
                pilotnumber = request.form.get("pilotnumber", "").strip()
                name = request.form.get("name")
                lastname = request.form.get("lastname")

                # Validation des champs
                if not all([email, password, pilotnumber, name, lastname]):
                    flash("All fields are required")
                    return redirect(url_for("register"))

                # Convertir pilotnumber en integer
                try:
                    pilotnumber = int(pilotnumber)
                except ValueError:
                    flash("Pilot number must be a valid number")
                    return redirect(url_for("register"))

                # Vérifier si l'email existe déjà
                if Pilot.query.filter_by(pilot_email=email).first():
                    flash("This email is already registered")
                    return redirect(url_for("register"))

                # UNE SEULE vérification du numéro de pilote
                existing_pilot = Pilot.query.filter_by(pilot_number=pilotnumber).first()

                if existing_pilot:
                    # Le numéro existe → afficher le pop-up
                    session['temp_register_data'] = {
                        'email': email,
                        'password': password,
                        'pilotnumber': pilotnumber,
                        'name': name,
                        'lastname': lastname
                    }
                    return render_template("register.html",
                                           show_popup=True,
                                           pilotnumber=pilotnumber,
                                           form_data=session['temp_register_data'])

                # Le numéro n'existe pas → créer directement
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
                return redirect(url_for("login"))

        return render_template("register.html", show_popup=False)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            userlogin = request.form["email"]
            password = request.form["password"]

            user = Pilot.query.filter_by(pilot_email=userlogin).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Invalid username or password")
                return redirect(url_for("login"))
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out")
        return redirect(url_for("login"))


def create_app():
    """
    Create and configure an instance of the Flask application.
    :return: The application ready
    """
    app = Flask(__name__)

    app.config.from_object(Setup)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "login"

    register_routes(app)

    @app.route("/")
    @login_required
    def home():
        return redirect(url_for("analytics.index", pilot_number=current_user.pilot_number))

    app.register_blueprint(analytics)

    return app


app = create_app()
if __name__ == "__main__":
    app.run(debug=True)