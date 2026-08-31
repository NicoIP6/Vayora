from flask import render_template, request, Blueprint
from shared.database_file.oltp_models import Weatherforecast, db
from datetime import datetime, time, date

weather_bp = Blueprint("weather_bp", __name__)

DEFAULT_WEATHER_PLACE = "les sept meuses"


@weather_bp.route("/api/weather")
def api_weather():

    selected_place = (
        request.args.get("place", "").strip()
        or DEFAULT_WEATHER_PLACE
    )

    selected_date = (
        request.args.get("date", "").strip()
        or date.today().isoformat()
    )

    query = (
        db.session.query(Weatherforecast)
        .with_entities(
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
            Weatherforecast.wind_direction_120m,
        )
        .filter(
            Weatherforecast.weather_place == selected_place
        )
    )

    try:
        target = datetime.strptime(
            selected_date,
            "%Y-%m-%d"
        ).date()

        day_start = datetime.combine(
            target,
            time.min
        )

        day_end = datetime.combine(
            target,
            time.max
        )

        query = query.filter(
            Weatherforecast.weather_date >= day_start,
            Weatherforecast.weather_date <= day_end,
        )

    except ValueError:
        pass

    weather = (
        query
        .order_by(Weatherforecast.weather_date.asc())
        .first()
    )

    return render_template(
        "partials/weather_grid.html",
        weather=weather
    )