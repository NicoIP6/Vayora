from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from shared.database_file.set_up import Setup
from flask_app.statistics import analytics
from flask_app.login_flask import login_bp
from flask_app.registering import registering_bp
from flask_app.weather_route import weather_bp
from shared.database_file.oltp_models import Weatherforecast, login_manager, db, bcrypt, Pilot
from datetime import datetime, time, date as date_type
import random
from sqlalchemy import text
from threading import Thread
from bokeh.server.server import Server
from dashboard.dashboard import create_dashboard
from bokeh.embed import server_document


def dashboard_app(doc):
    panel = create_dashboard()
    panel.server_doc(doc)


def start_bokeh_server():
    try:
        server = Server(
            {"/dashboard": dashboard_app},
            port=5006,
            allow_websocket_origin=["localhost:5000", "127.0.0.1:5000"]
        )
        server.start()
        server.io_loop.start()
    except OSError:
        pass

Thread(target=start_bokeh_server, daemon=True).start()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Setup)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "login_bp.login"

    @app.route("/")
    def home():

        raw_places = (
            db.session.query(Weatherforecast.weather_place)
            .distinct()
            .order_by(Weatherforecast.weather_place)
            .all()
        )
        locations = [{"name": row[0]} for row in raw_places]

        selected_place = request.args.get("place", "").strip()
        selected_date = request.args.get("date", "").strip()

        predictions = []
        selected_ai_date = request.args.get("ai_date", "").strip()
        selected_ai_place = request.args.get("ai_place", "").strip()

        if current_user.is_authenticated and selected_ai_date:
            try:
                datetime.strptime(selected_ai_date, "%Y-%m-%d")  # validation
                place_filter = f"AND weather_place = '{selected_ai_place}'" if selected_ai_place else ""
                sql = f"""
                        SELECT weather_place, score_vol, wind_speed_120m
                        FROM predictions_flight
                        WHERE date_jour = '{selected_ai_date}'
                          AND is_flyable = True
                          {place_filter}
                        ORDER BY score_vol DESC
                    """
                result = db.session.execute(text(sql))
                predictions = result.fetchall()
            except ValueError:
                pass

        panel_script = server_document(
            "http://localhost:5006/dashboard"
        )

        return render_template(
            "home.html",
            locations=locations,
            selected_place=selected_place,
            selected_date=selected_date,
            predictions=predictions,
            selected_ai_date=selected_ai_date,
            selected_ai_place=selected_ai_place,
            panel_script=panel_script,
        )

    app.register_blueprint(analytics)
    app.register_blueprint(login_bp)
    app.register_blueprint(registering_bp)
    app.register_blueprint(weather_bp)
    return app


app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
