import pandas as pd
from flask import render_template, redirect, url_for, flash, Blueprint, send_file
from flask_login import login_required
from sqlalchemy.orm import joinedload
import io
from shared.database_file.dwh_models import *


analytics = Blueprint('analytics', __name__)


def _to_decimal_hours(t):
    """Convertit un objet time Python en heures décimales."""
    if t is None:
        return 0
    return t.hour + t.minute / 60


def _build_df(pilot_id):
    flights = (
        db.session.query(FactFlight)
        .options(
            joinedload(FactFlight.dim_date),
            joinedload(FactFlight.dim_time),
            joinedload(FactFlight.dim_pilot),
            joinedload(FactFlight.dim_takeoff)
        )
        .filter(FactFlight.fact_flight_pilot == pilot_id)
        .all()
    )

    data = []
    for flight in flights:
        data.append({
            "pilot_number": flight.dim_pilot.dim_pilot_bk,
            "date":         flight.dim_date.full_date,
            "takeoff":      flight.dim_takeoff.dim_takeoff_name,
            "airtime":      flight.fact_flight_airtime,
            "distance":     flight.fact_flight_distance,
            "season":       flight.dim_date.season,
        })

    df = pd.DataFrame(data)

    if not df.empty:
        df["year"] = pd.to_datetime(df["date"]).dt.year

    return df


@analytics.route('/analytics/<int:pilot_number>', methods=['GET', 'POST'])
@login_required
def index(pilot_number):
    pilot = DimPilot.query.filter_by(dim_pilot_bk=pilot_number).first()
    if not pilot:
        flash("Pilote introuvable", "error")
        return redirect(url_for("home"))

    pilot_id = pilot.dim_pilot_bk
    df = _build_df(pilot_id)

    if df.empty:
        flash("Aucun vol trouvé pour ce pilote.", "warning")
        return render_template("index.html",
            total_flights=0, total_distance=0, max_distance=0,
            mean_distance=0, total_airtime="0h00", best_season="—",
            seasons=[], distances=[],
            years_labels=[], flights_per_year=[], hours_per_year=[],
            takeoff_names=[], takeoff_max_dist=[],
            flights_rows=[],
        )

    # ── Globaux ──────────────────────────────────────────────────────────────
    total_flights  = len(df)
    total_distance = int(df["distance"].sum())
    max_distance   = int(df["distance"].max())
    mean_distance  = round(float(df["distance"].mean()), 1)

    df["airtime_h"] = df["airtime"].apply(_to_decimal_hours)
    total_h = df["airtime_h"].sum()
    total_airtime = f"{int(total_h)}h{int((total_h % 1) * 60):02d}"

    # ── Par saison ────────────────────────────────────────────────────────────
    by_season = (
        df.groupby("season")
        .agg(total_distance=("distance", "sum"))
        .reset_index()
    )
    seasons   = by_season["season"].tolist()
    distances = by_season["total_distance"].astype(int).tolist()

    best_season = by_season.loc[by_season["total_distance"].idxmax(), "season"] \
        if not by_season.empty else "—"

    # ── Par année ─────────────────────────────────────────────────────────────
    by_year = (
        df.groupby("year")
        .agg(flight_count=("distance", "count"), total_hours=("airtime_h", "sum"))
        .reset_index()
        .sort_values("year")
    )
    years_labels     = [str(int(y)) for y in by_year["year"].tolist()]
    flights_per_year = by_year["flight_count"].tolist()
    hours_per_year   = [round(h, 1) for h in by_year["total_hours"].tolist()]

    # ── Par décollage ─────────────────────────────────────────────────────────
    by_takeoff = (
        df.groupby("takeoff")["distance"]
        .max()
        .sort_values(ascending=True)
        .tail(5)
    )
    takeoff_names    = by_takeoff.index.tolist()
    takeoff_max_dist = by_takeoff.astype(int).tolist()

    # ── Détail des vols (tableau) ─────────────────────────────────────────────
    flights_rows = (
        df.sort_values("date", ascending=False)
        .drop(columns=["airtime_h", "year"], errors="ignore")
        .to_dict("records")
    )

    return render_template("index.html",
        total_flights    = total_flights,
        total_distance   = total_distance,
        max_distance     = max_distance,
        mean_distance    = mean_distance,
        total_airtime    = total_airtime,
        best_season      = best_season,
        seasons          = seasons,
        distances        = distances,
        years_labels     = years_labels,
        flights_per_year = flights_per_year,
        hours_per_year   = hours_per_year,
        takeoff_names    = takeoff_names,
        takeoff_max_dist = takeoff_max_dist,
        flights_rows     = flights_rows,
    )


@analytics.route('/analytics/<int:pilot_number>/download', methods=['GET'])
@login_required
def download_csv(pilot_number):
    pilot = DimPilot.query.filter_by(dim_pilot_bk=pilot_number).first()
    if not pilot:
        flash("Pilote introuvable", "error")
        return redirect(url_for("analytics.index", pilot_number=pilot_number))

    df = _build_df(pilot.dim_pilot_bk)

    if df.empty:
        flash("Aucun vol trouvé", "warning")
        return redirect(url_for("analytics.index", pilot_number=pilot_number))

    df["airtime_h"] = df["airtime"].apply(_to_decimal_hours)

    total_h       = df["airtime_h"].sum()
    total_airtime = f"{int(total_h)}h{int((total_h % 1) * 60):02d}"

    by_year = (
        df.groupby("year")
        .agg(flight_count=("distance", "count"), total_hours=("airtime_h", "sum"))
        .reset_index()
        .sort_values("year")
    )

    output = io.StringIO()

    output.write("=== STATISTIQUES GLOBALES ===\n")
    pd.DataFrame({
        "Statistique": [
            "Nombre total de vols",
            "Distance totale (km)",
            "Distance max (km)",
            "Distance moyenne (km)",
            "Temps total en l'air",
        ],
        "Valeur": [
            len(df),
            int(df["distance"].sum()),
            int(df["distance"].max()),
            round(float(df["distance"].mean()), 2),
            total_airtime,
        ]
    }).to_csv(output, index=False)

    output.write("\n=== VOLS PAR ANNÉE ===\n")
    by_year.rename(columns={
        "year": "Année",
        "flight_count": "Nombre vols",
        "total_hours": "Heures vol"
    }).to_csv(output, index=False)

    output.write("\n=== DÉTAIL DES VOLS ===\n")
    export = df[["date", "takeoff", "distance", "airtime", "season"]].copy()
    export.columns = ["Date", "Décollage", "Distance (km)", "Temps en l'air", "Saison"]
    export.to_csv(output, index=False)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"pilot_{pilot_number}_analytics.csv"
    )
