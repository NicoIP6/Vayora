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
    app = Flask(__name__)

    app.config.from_object(Setup)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "login_bp.login"

    @app.route("/")
    def home():
        # ── Récupérer les lieux distincts pour le sélecteur ─────────────────

        raw_places = (
            db.session.query(Weatherforecast.weather_place)
            .distinct()
            .order_by(Weatherforecast.weather_place)
            .all()
        )
        locations = [{"name": row[0]} for row in raw_places]

        # ── Lire les filtres GET ─────────────────────────────────────────────
        selected_place = request.args.get("place", "").strip()
        selected_date  = request.args.get("date", "").strip()

        # ── Construire la requête météo ──────────────────────────────────────
        query = db.session.query(Weatherforecast).with_entities(
            # ⚠️ Adapter : liste des colonnes à afficher selon votre modèle Weatherforecast
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
        )

        if selected_place:

            query = query.filter(Weatherforecast.weather_place == selected_place)

        if selected_date:
            try:
                target = datetime.strptime(selected_date, "%Y-%m-%d").date()
                day_start = datetime.combine(target, time.min)
                day_end   = datetime.combine(target, time.max)
                # ⚠️ Adapter : Weatherforecast.weather_date selon votre modèle
                query = query.filter(
                    Weatherforecast.weather_date >= day_start,
                    Weatherforecast.weather_date <= day_end,
                )
            except ValueError:
                pass  # date invalide → on ignore le filtre
        else:
            # Pas de filtre date : on prend aujourd'hui
            today_start = datetime.combine(datetime.now().date(), time.min)
            today_end   = datetime.combine(datetime.now().date(), time.max)
            query = query.filter(
                Weatherforecast.weather_date >= today_start,
                Weatherforecast.weather_date <= today_end,
            )

        forecasts = query.all()

        # Si lieu sélectionné → on prend le plus récent ; sinon aléatoire
        if selected_place and forecasts:

            weather = forecasts[-1]
        else:
            weather = random.choice(forecasts) if forecasts else None

        return render_template(
            "home.html",
            weather        = weather,
            locations      = locations,
            selected_place = selected_place,
            selected_date  = selected_date,
        )

    app.register_blueprint(analytics)
    app.register_blueprint(login_bp)
    app.register_blueprint(registering_bp)

    return app


app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
