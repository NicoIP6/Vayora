from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from shared.database_file.set_up import Setup
from flask_app.statistics import analytics
from flask_app.login_flask import login_bp
from flask_app.registering import registering_bp
from shared.database_file.oltp_models import Weatherforecast, login_manager, db, bcrypt, Pilot
from datetime import datetime, time, date as date_type
import random
from sqlalchemy import text


def create_app():
    app = Flask(__name__)

    app.config.from_object(Setup)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "login_bp.login"

    @app.route("/")
    def home():
        # ── Lieux distincts pour les sélecteurs ─────────────────────────────
        raw_places = (
            db.session.query(Weatherforecast.weather_place)
            .distinct()
            .order_by(Weatherforecast.weather_place)
            .all()
        )
        locations = [{"name": row[0]} for row in raw_places]

        # ── Filtres météo (section du haut) ─────────────────────────────────
        selected_place = request.args.get("place", "").strip()
        selected_date  = request.args.get("date",  "").strip()

        # ── Requête météo ────────────────────────────────────────────────────
        query = db.session.query(Weatherforecast).with_entities(
            Weatherforecast.weather_date,
            Weatherforecast.weather_place,
            Weatherforecast.temperature_120m,
            Weatherforecast.precipitation_probability,
            Weatherforecast.cloud_cover,
            Weatherforecast.relative_humidity_950hpa,
            Weatherforecast.pressure_msl,
            Weatherforecast.surface_pressure,
            Weatherforecast.cape,
            Weatherforecast.boundary_layer_height,
            Weatherforecast.lifted_index,
            Weatherforecast.convective_inhibition,
            Weatherforecast.wind_speed_120m,
            Weatherforecast.wind_direction_120m
        )

        if selected_place:
            query = query.filter(Weatherforecast.weather_place == selected_place)

        if selected_date:
            try:
                target    = datetime.strptime(selected_date, "%Y-%m-%d").date()
                day_start = datetime.combine(target, time.min)
                day_end   = datetime.combine(target, time.max)
                query = query.filter(
                    Weatherforecast.weather_date >= day_start,
                    Weatherforecast.weather_date <= day_end,
                )
            except ValueError:
                pass
        else:
            today_start = datetime.combine(datetime.now().date(), time.min)
            today_end   = datetime.combine(datetime.now().date(), time.max)
            query = query.filter(
                Weatherforecast.weather_date >= today_start,
                Weatherforecast.weather_date <= today_end,
            )

        forecasts = query.all()
        weather = forecasts[-1] if (selected_place and forecasts) else (
            random.choice(forecasts) if forecasts else None
        )

        # ── Prédictions IA (section du bas, utilisateurs connectés) ─────────
        predictions       = []
        selected_ai_date  = request.args.get("ai_date",  "").strip()
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

        return render_template(
            "home.html",
            weather           = weather,
            locations         = locations,
            selected_place    = selected_place,
            selected_date     = selected_date,
            predictions       = predictions,
            selected_ai_date  = selected_ai_date,
            selected_ai_place = selected_ai_place,
        )

    app.register_blueprint(analytics)
    app.register_blueprint(login_bp)
    app.register_blueprint(registering_bp)

    return app


app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
