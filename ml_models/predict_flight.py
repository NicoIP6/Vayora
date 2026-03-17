import pandas as pd
import json
import numpy as np
import pandas as pd
from shared.database_file.set_up import Setup
import joblib
import os



FEATURES = [
    'wind_speed_120m', 'precipitation', 'wind_diff_ref',
    'wind_speed_950hpa', 'wind_speed_850hpa', 'wind_speed_800hpa',
    'wind_speed_700hpa', 'wind_speed_600hpa'
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, 'flyable_day', 'model_parapente.pkl')
ORIENTATION_PATH = os.path.join(BASE_DIR, 'flyable_day', 'orientations_sites.pkl')

model = joblib.load(MODEL_PATH)
orientations = joblib.load(ORIENTATION_PATH)


def get_angle_diff(a, b):
    diff = np.abs(a - b)
    return np.where(diff > 180, 360 - diff, diff)


def run_predictions():

    con = Setup().get_duckdb_conn()


    query = """
            SELECT *,
                   CAST(weather_date AS DATE) as date_jour
            FROM vayora.weather_forecast wf
            WHERE hour (weather_date) BETWEEN 10 \
              AND 18
              AND date_jour BETWEEN current_date \
              AND current_date + INTERVAL 2 DAY \
            """
    df_forecast = con.execute(query).df()

    df_daily = df_forecast.groupby(['weather_place', 'date_jour']).median(numeric_only=True).reset_index()

    # 4. Feature Engineering (Calcul de l'écart au vent)
    df_daily['deco_orientation_ref'] = df_daily['weather_place'].map(orientations)
    df_daily['wind_diff_ref'] = get_angle_diff(
        df_daily['wind_direction_120m'],
        df_daily['deco_orientation_ref']
    )

    X = df_daily[FEATURES].add_suffix('_x')
    X = X.rename(columns={'wind_diff_ref_x': 'wind_diff_ref'})
    df_daily['is_flyable'] = model.predict(X).astype(bool)

    df_daily['score_vol'] = model.predict_proba(X)[:, 1]


    con.execute("""CREATE OR REPLACE TABLE vayora.predictions_flight AS SELECT * FROM df_daily""")

    print(f"Prédictions terminées pour {len(df_daily)} créneaux (3 jours).")


if __name__ == "__main__":
    run_predictions()