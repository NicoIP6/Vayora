from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from shared.database_file.set_up import Setup
from flask_app.statistics import analytics
from flask_app.login_flask import login_bp
from flask_app.registering import registering_bp
from shared.database_file.oltp_models import Weatherforecast, login_manager, db, bcrypt
from datetime import datetime, time
import random


def create_app():
    """
    Create and configure an instance of the Flask flask_app.
    :return: The flask_app ready
    """
    app = Flask(__name__)

    app.config.from_object(Setup)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "login"


    @app.route("/")
    def home():
        today_start = datetime.combine(datetime.now().date(), time.min)
        today_end = datetime.combine(datetime.now().date(), time.max)
        forecasts = Weatherforecast.query.with_entities(
            Weatherforecast.weather_date,
            Weatherforecast.weather_place,
            Weatherforecast.temperature_120m,
            Weatherforecast.precipitation,
            Weatherforecast.pressure_msl,
            Weatherforecast.cape,
            Weatherforecast.boundary_layer_height,
            Weatherforecast.lifted_index,
            Weatherforecast.convective_inhibition,
            Weatherforecast.wind_speed_120m
        ).filter(
            Weatherforecast.weather_date >= today_start,
            Weatherforecast.weather_date <= today_end
        ).all()

        random_weather = random.choice(forecasts) if forecasts else None
        return render_template("home.html", weather=random_weather)

    app.register_blueprint(analytics)
    app.register_blueprint(login_bp)
    app.register_blueprint(registering_bp)

    return app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True)