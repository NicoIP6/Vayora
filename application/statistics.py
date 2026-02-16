import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint, send_file
from flask_login import login_user, logout_user, login_required, current_user
from application.set_up import Setup
from application.extensions import db, bcrypt, login_manager
from db.oltp_models import *
from db.dwh_models import *
from sqlalchemy.orm import joinedload
import io


analytics = Blueprint('analytics', __name__)

@analytics.route('/analytics/<int:pilot_number>', methods=['GET', 'POST'])
def index(pilot_number):

    pilot = DimPilot.query.filter_by(dim_pilot_bk=pilot_number).first()
    pilot_id = pilot.dim_pilot_sk
    flights = (
        db.session.query(FactFly)
        .options(
            joinedload(FactFly.dim_date),
            joinedload(FactFly.dim_time),
            joinedload(FactFly.dim_pilot),
            joinedload(FactFly.dim_takeoff)
        )
        .filter(FactFly.fact_fly_pilot == pilot_id)
        .all()
    )
    data = []
    for flight in flights:
        data.append({
            "pilot number": flight.dim_pilot.dim_pilot_bk,
            "date" : flight.dim_date.full_date,
            "takeoff" : flight.dim_takeoff.dim_takeoff_name,
            "airtime" : flight.fact_fly_airtime,
            "distance" : flight.fact_fly_distance,
            "season" : flight.dim_date.season,
        })
    df = pd.DataFrame(data)
    df_grouped = df.groupby("season").agg(
        flight_count=("distance", "count"),
        total_distance=("distance", "sum")
    ).reset_index()

    # Convert to list for de plotly in JS ---> problem with json translate
    seasons = df_grouped["season"].tolist()
    distances = df_grouped["total_distance"].astype(int).tolist()

    return render_template("index.html", seasons=seasons, distances=distances)

@analytics.route('/analytics/<int:pilot_number>/download', methods=['GET'])
@login_required
def download_csv(pilot_number):

    pilot = DimPilot.query.filter_by(dim_pilot_bk=pilot_number).first()
    if not pilot:
        flash("Pilote introuvable", "danger")
        return redirect(url_for("analytics.index", pilot_number=pilot_number))

    pilot_id = pilot.dim_pilot_sk

    flights = (
        db.session.query(FactFly)
        .options(
            joinedload(FactFly.dim_date),
            joinedload(FactFly.dim_time),
            joinedload(FactFly.dim_pilot),
            joinedload(FactFly.dim_takeoff)
        )
        .filter(FactFly.fact_fly_pilot == pilot_id)
        .all()
    )

    data = []
    for flight in flights:
        data.append({
            "Pilot number": flight.dim_pilot.dim_pilot_bk,
            "Date": flight.dim_date.full_date,
            "Takeoff": flight.dim_takeoff.dim_takeoff_name,
            "Airtime (min)": flight.fact_fly_airtime,
            "Distance (km)": flight.fact_fly_distance,
            "Season": flight.dim_date.season,
        })

    df = pd.DataFrame(data)

    if df.empty:
        flash("Aucun vol trouvé", "warning")
        return redirect(url_for("analytics.index", pilot_number=pilot_number))


    # Extract hours
    hours = df['Airtime (min)'].apply(lambda x: x.hour)

    # Extract minutes
    minutes = df['Airtime (min)'].apply(lambda x: x.minute)

    total_hours = hours.sum()
    total_minutes = minutes.sum()

    final_hours = total_hours + (total_minutes // 60)
    final_minutes = total_minutes % 60

    formatted_airtime = f"{final_hours}h{final_minutes:02d}"

    total_flights = len(df)
    total_distance = df["Distance (km)"].sum()
    max_distance = df["Distance (km)"].max()
    mean_distance = df["Distance (km)"].mean()

    stats_df = pd.DataFrame({
        "Statistique": [
            "Nombre total de vols",
            "Distance totale (km)",
            "Distance max (km)",
            "Distance moyenne (km)",
            "Temps total en l'air (min)"
        ],
        "Valeur": [
            total_flights,
            int(total_distance),
            int(max_distance),
            round(mean_distance, 2),
            formatted_airtime
        ]
    })


    output = io.StringIO()

    output.write("=== STATISTIQUES ===\n")
    stats_df.to_csv(output, index=False)

    output.write("\n=== RECAP DES VOLS ===\n")
    df.to_csv(output, index=False)

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"pilot_{pilot_number}_analytics.csv"
    )
