import duckdb
import logging
from datetime import datetime as dt


logging.basicConfig(filename='../logging/fill_dw.log', level=logging.INFO)
logger = logging.getLogger(__name__)



def setup_duckdb(*args):
    """

    :param args: Every args must be a tuple withe db name or alias and the connexion path.
    Check duckdb documentation to know the correct format.
    For exemple with postgres : postgresql://username:password@host:port/dbname

    :return: a duckdb connexion
    """

    try:
        conn = duckdb.connect()

        conn.execute("INSTALL postgres")
        conn.execute("LOAD postgres")

        for db in args:
            if not isinstance(db, tuple):
                print("One or more arguments given to the function weren't a tuple")
                return -1
            else:
                conn.execute(f"ATTACH '{db[1]}' as {db[0]} (TYPE postgres)")

        return conn

    except Exception as e:
        print(f"Something went wrong while connecting to duckdb : Exception {e}")


def fill_dim_pilot(db_conn):
    """

    :param db_conn:
    :return:
    """
    time_use = dt.now()
    formated_time = time_use.strftime("%d-%m-%Y %H:%M:%S")
    try:
        req = """SELECT vp.pilot_number, vp.pilot_maxdistance
                  FROM vayora.pilot vp
                  WHERE vp.pilot_number NOT IN (SELECT dim_pilot_pilotnumber FROM dwh.dim_pilot)
                """

        count_req = f"SELECT COUNT(*) AS n FROM ({req})"
        rows_to_insert = db_conn.execute(count_req).fetchone()[0]

        db_conn.execute("BEGIN TRANSACTION")
        db_conn.execute(f"INSERT INTO dwh.dim_pilot {req}")

        db_conn.commit()
        logger.info(f"{formated_time} - Table dim_pilot has been successfully filled with {rows_to_insert} pilots")
    except Exception as e:
        db_conn.rollback()
        logger.error(f"{formated_time} - Insert in dim_pilot table failed : {e}")


def fill_dim_takeoff(db_conn):
    """

    :param db_conn:
    :return:
    """
    time_use = dt.now()
    formated_time = time_use.strftime("%d-%m-%Y %H:%M:%S")
    try:
        req = """SELECT vt.takeoff_name
                  FROM vayora.takeoff vt
                  WHERE vt.takeoff_name NOT IN (SELECT dim_takeoff_name FROM dwh.dim_takeoff) 
                """

        count_req = f"SELECT COUNT(*) AS n FROM ({req})"
        rows_to_insert = db_conn.execute(count_req).fetchone()[0]

        db_conn.execute("BEGIN TRANSACTION")
        db_conn.execute(f"INSERT INTO dwh.dim_takeoff (dim_takeoff_name) {req}")

        db_conn.commit()
        logger.info(f"{formated_time} - Table dim_takeoff has been successfully filled with {rows_to_insert} takeoff")
    except Exception as e:
        db_conn.rollback()
        logger.error(f"{formated_time} - Insert in dim_takeoff table failed : {e}")


def fill_dim_weather(db_conn):
    """

    :param db_conn:
    :return:
    """
    time_use = dt.now()
    formated_time = time_use.strftime("%d-%m-%Y %H:%M:%S")
    cols = db_conn.execute(""" SELECT column_name
                               FROM dwh.information_schema.columns
                               WHERE table_schema = 'public'
                                 AND table_name = 'dim_weather'
                                 AND column_name <> 'dim_weather_sk'
                                 """).fetchall()
    col_list = ", ".join([c[0] for c in cols])
    print(col_list)
    try:
        req = """SELECT * EXCLUDE (fw.weather_date, fw.weather_place)
                 FROM forecast.weather fw
                 WHERE fw.weather_id NOT IN (SELECT dim_weather_bk FROM dwh.dim_weather)
                """

        count_req = f"SELECT COUNT(*) AS n FROM ({req})"
        rows_to_insert = db_conn.execute(count_req).fetchone()[0]

        db_conn.execute("BEGIN TRANSACTION")
        db_conn.execute(f"""INSERT INTO dwh.dim_weather ({col_list}) {req}""")

        db_conn.commit()
        logger.info(f"{formated_time} - Table dim_weather has been successfully filled with {rows_to_insert} weather rows")

    except Exception as e:
        db_conn.rollback()
        logger.error(f"{formated_time} - Insert in dim_weather table failed : {e}")


# oltp_conn = ("vayora", 'postgresql://postgres:passwordfortest@localhost:5432/vayora_test')
stating_conn = ("forecast", 'postgresql://postgres:passwordfortest@localhost:5432/vayora_weather_staging')
dwh_conn = ("dwh", 'postgresql://postgres:passwordfortest@localhost:5432/vayora_dw')


postgres_conn = setup_duckdb(stating_conn, dwh_conn)

# fill_dim_pilot(postgres_conn)
# fill_dim_takeoff(postgres_conn)
# fill_dim_flight(postgres_conn)
fill_dim_weather(postgres_conn)
