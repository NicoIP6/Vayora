from flask import render_template, request, Blueprint
from shared.database_file.oltp_models import Weatherforecast, db
from datetime import datetime, time
import random

weather_bp = Blueprint("weather_bp", __name__)

@weather_bp.route("/api/weather")
def api_weather():
    # ── Filtres météo (section du haut) ─────────────────────────────────
    selected_place = request.args.get("place", "").strip()
    selected_date = request.args.get("date", "").strip()

    # ── Requête météo principale ─────────────────────────────────────────
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
            target = datetime.strptime(selected_date, "%Y-%m-%d").date()
            day_start = datetime.combine(target, time.min)
            day_end = datetime.combine(target, time.max)
            query = query.filter(
                Weatherforecast.weather_date >= day_start,
                Weatherforecast.weather_date <= day_end,
            )
        except ValueError:
            pass
    else:
        today_start = datetime.combine(datetime.now().date(), time.min)
        today_end = datetime.combine(datetime.now().date(), time.max)
        query = query.filter(
            Weatherforecast.weather_date >= today_start,
            Weatherforecast.weather_date <= today_end,
        )

    forecasts = query.all()
    weather = forecasts[-1] if (selected_place and forecasts) else (
        random.choice(forecasts) if forecasts else None
    )

    # On ne renvoie que le composant avec la variable nécessaire
    return render_template("partials/weather_grid.html", weather=weather)