from sqlalchemy import create_engine, text, inspect
import pandas as pd
import numpy as np
from pathlib import Path

psql_oltp = create_engine('postgresql+psycopg2://postgres:passwordfortest@localhost:5432/vayora_test')
psql_staging = create_engine('postgresql+psycopg2://postgres:passwordfortest@localhost:5432/vayora_weather_staging')

with psql_oltp.connect() as conn:

    req = conn.execute(text('SELECT tkf.takeoff_name FROM takeoff tkf'))
    raw = [i[0] for i in req.fetchall()]


inspector = inspect(psql_staging)
columns_db = [col["name"] for col in inspector.get_columns("weather")]
path = '../data/Weather_Data/Open-Meteo/'

for tkf in raw:

    file = Path(f"{path}{tkf}.csv")

    if file.exists():

        print(50*'-')
        print(f"Loading {tkf}")
        print(21 * '-' + " start " + 22 * '-')

        temp_df = pd.read_csv(file, encoding='utf-8')
        temp_df.rename(columns={'date': 'weather_date'}, inplace=True)
        temp_df = temp_df[temp_df['weather_date'] != '0']
        temp_df = temp_df[temp_df['weather_date'].notna()]
        temp_df.reset_index(drop=True, inplace=True)

        temp_df['weather_date'] = pd.to_datetime(temp_df['weather_date'], format='%Y-%m-%d %H:%M:%S%z', utc=True)
        temp_df['weather_place'] = tkf
        temp_df.columns = temp_df.columns.str.replace('"', '').str.strip()
        temp_df.columns = temp_df.columns.str.lower()
        temp_df.to_sql('weather', con= psql_staging, if_exists="append", method='multi', chunksize=5000, index= False)
