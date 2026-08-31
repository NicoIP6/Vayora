import duckdb
import pandas as pd
import re
import numpy as np
from pathlib import Path
from shared.database_file.set_up import Setup


COLUMN_RULES = {
    r'pressure|pres': (700.0, 1085.0),
    r'temp|temperature|tmp': (-60.0,   60.0),
    r'humid|humidity|rh': (0.0, 100.0),
    r'cloud|cover|coverage': (0.0, 100.0),
    r'wind.?speed|wspd|speed': (0.0, 250.0),
    r'wind.?dir|wdir|direction|deg': (0.0, 360.0),
    r'dewpoint|dew': (-60.0, 60.0),
    r'precip|rain|rainfall': (0.0, 500.0),
    r'snow': (0.0, 200.0)
}

def get_integer_digit_count(val, valid_range):
    """Retourne le nombre de chiffres de la partie entière si val est déjà clean."""
    low, high = valid_range
    if low <= val <= high:
        return len(str(int(val)))
    return None

def fix_ambiguous_value(val, n_integer_digits):
    s = str(int(val))
    if len(s) <= n_integer_digits:
        return float(val)  # déjà clean
    integer_part = s[:n_integer_digits]
    decimal_part = s[n_integer_digits:]
    return float(f"{integer_part}.{decimal_part}")


def fix_column(series: pd.Series, valid_range: tuple) -> pd.Series:
    low, high = valid_range
    result = series.copy().astype(float)

    # Étape 1 : identifier les valeurs déjà dans la plage (clean) vs à corriger
    is_clean = series.apply(lambda v: v is not None and not pd.isna(v) and low <= v <= high)

    # Étape 2 : pour chaque valeur ambiguë, chercher le voisin clean le plus proche
    for i in series.index:
        if series[i] is None or pd.isna(series[i]):
            continue

        n_digits = None

        # Cherche vers l'arrière
        for j in range(i - 1, series.index[0] - 1, -1):
            if is_clean[j]:
                n_digits = get_integer_digit_count(series[j], valid_range)
                break

        # Si pas trouvé, cherche vers l'avant
        if n_digits is None:
            for j in range(i + 1, series.index[-1] + 1):
                if is_clean[j]:
                    n_digits = get_integer_digit_count(series[j], valid_range)
                    break

        # Fallback : aucun voisin clean trouvé (cas extrême)
        if n_digits is None:
            result[i] = np.nan  # ou une valeur par défaut, à toi de voir
            continue

        result[i] = fix_ambiguous_value(series[i], n_digits)

    return result
def get_range_for_column(col_name: str) -> tuple | None:
    col_lower = col_name.lower()
    for pattern, value_range in COLUMN_RULES.items():
        if re.search(pattern, col_lower):
            return value_range
    return None


def fix_all_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        value_range = get_range_for_column(col)
        if value_range is None:
            continue  # colonne non reconnue, on touche pas
        print(f"Fixing '{col}' with range {value_range}")
        df[col] = fix_column(df[col], valid_range=value_range)
    return df

def insert_weather(db_name: str, table_name: str, df: pd.DataFrame, db_connection: duckdb.DuckDBPyConnection) -> int:
    """

    :param db_name:
    :param table_name:
    :param df:
    :param db_connection:
    :return:
    """
    try:
        fixed_df = fix_all_columns(df)
        cols = ', '.join(fixed_df.columns.tolist())
        db_connection.execute(f"INSERT INTO {db_name}.{table_name} ({cols}) SELECT * FROM fixed_df")
        print(f"{tkf} loaded ({len(fixed_df)} rows)")

        return 0

    except Exception as e:
        print(f"Error: {e} occured")

        return 1

if __name__ == "__main__":
    print("start fill weather")
    conn = Setup.get_duckdb_conn()

    takeoffs = conn.execute("SELECT tkf.takeoff_name FROM vayora.takeoff tkf").fetchall()
    raw = [i[0] for i in takeoffs]
    BASE_DIR = Path(__file__).resolve().parent.parent
    path = BASE_DIR / "data" / "Weather_Data" / "open-meteo"
    table_created = False
    weather_place = conn.execute("SELECT wth.weather_place FROM weather.weather_historic wth").fetchall()
    alr_exist = [i[0] for i in weather_place]

    try:
        for tkf in raw:

            print(f"building path : {tkf}\n")
            file = path / f"{tkf}.csv"

            if file.exists() and tkf not in alr_exist:

                print(50 * '-')
                print(f"Loading {tkf}")
                print(21 * '-' + " start " + 22 * '-' + "\n")
                file_str = str(file).replace("'", "''")
                tkf_escaped = tkf.replace("'", "''")

                temp = conn.execute(f"""
                    SELECT
                        CAST(CAST(date AS TIMESTAMPTZ) AT TIME ZONE 'UTC' AS TIMESTAMP) AS weather_date,
                        * EXCLUDE (date),
                        '{tkf_escaped}' AS weather_place
                    FROM read_csv_auto('{file_str}', 
                                        header=True,
                                        types={{'date': 'VARCHAR'}})
                    WHERE date IS NOT NULL
                      AND CAST(date AS VARCHAR) != '0'
                """).df()

                temp.columns = (
                    temp.columns
                    .str.replace('"', '')
                    .str.strip()
                    .str.lower()
                )
                insert_weather("weather", "weather_historic", temp, conn)
            else:
                print("\n" + 50 * '-')
                print(f"file for {tkf} not found or {tkf} already exist")
                print(50 * '-')
    except Exception as e:
        print(f"Error: {e} occured")
