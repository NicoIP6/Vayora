import logging
from datetime import datetime as dt


logging.basicConfig(filename='../logging/dwh.log', level=logging.INFO)
logger = logging.getLogger(__name__)


def fill_dim_pilot(db_conn):
    """

    :param db_conn: must be a duck db connexion

    """
    time_use = dt.now()
    formated_time = time_use.strftime("%d-%m-%Y %H:%M:%S")
    db_conn.execute("BEGIN TRANSACTION")
    try:
        req = """SELECT vp.pilot_number, vp.pilot_maxdistance
                  FROM vayora.pilot vp
                  WHERE vp.pilot_number NOT IN (SELECT dim_pilot_bk FROM dwh.dim_pilot)
                """

        count_req = f"SELECT COUNT(*) AS n FROM ({req})"
        rows_to_insert = db_conn.execute(count_req).fetchone()[0]

        db_conn.execute(f"INSERT INTO dwh.dim_pilot (dim_pilot_bk, dim_pilot_maxdistance) {req}")

        db_conn.commit()

        rows_inserted = rows_to_insert - db_conn.execute(count_req).fetchone()[0]

        logger.info(f"{formated_time} - Table dim_pilot has been successfully filled with {rows_to_insert} pilots")

        return rows_inserted

    except Exception as e:
        db_conn.rollback()
        logger.error(f"{formated_time} - Insert in dim_pilot table failed : {e}")
        raise


def fill_dim_takeoff(db_conn):
    """

    :param db_conn:
    :return: number of takeoff inserted
    """
    time_use = dt.now()
    formated_time = time_use.strftime("%d-%m-%Y %H:%M:%S")

    db_conn.execute("BEGIN TRANSACTION")

    try:
        req = """SELECT vt.takeoff_id, vt.takeoff_name
                  FROM vayora.takeoff vt
                  WHERE vt.takeoff_id NOT IN (SELECT dim_takeoff_bk FROM dwh.dim_takeoff) 
                """

        count_req = f"SELECT COUNT(*) AS n FROM ({req})"

        rows_to_insert = db_conn.execute(count_req).fetchone()[0]

        db_conn.execute(f"INSERT INTO dwh.dim_takeoff (dim_takeoff_bk, dim_takeoff_name) {req}")
        db_conn.commit()

        rows_inserted = rows_to_insert - db_conn.execute(count_req).fetchone()[0]
        logger.info(f"{formated_time} - Table dim_takeoff has been successfully filled with {rows_to_insert} takeoff")

        return rows_inserted

    except Exception as e:
        db_conn.rollback()
        logger.error(f"{formated_time} - Insert in dim_takeoff table failed : {e}")
        raise


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
        rows_inserted = rows_to_insert - db_conn.execute(count_req).fetchone()[0]
        logger.info(f"{formated_time} - Table dim_weather has been successfully filled with {rows_to_insert} weather rows")

        return rows_inserted

    except Exception as e:
        db_conn.rollback()
        logger.error(f"{formated_time} - Insert in dim_weather table failed : {e}")
        raise
