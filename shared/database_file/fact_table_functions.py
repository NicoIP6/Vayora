import logging
from datetime import datetime as dt

logger = logging.getLogger(__name__)

def fill_fact_flight(db_conn):
    """
    Fill the fact_flight table in the data warehouse.

    Process :
    1. Selection of new flights (NOT EXISTS)
    2. Joins with all dimensions to retrieve the SK
    3. Date/time transformation into digital keys
    4. Insertion in fact_flight

    :param db_conn: DuckDB connexion with attached database
    :return: Number of lines inserted, or -1 in case of error
    """
    start_time = dt.now()

    try:
        logger.info("=" * 70)
        logger.info("Start loading fact_flight table")
        logger.info("=" * 70)

        count_req = """
                    SELECT COUNT(*) AS n
                    FROM vayora.flight vf
                    ANTI JOIN vayora_dw.fact_flight ff ON ff.fact_flight_bk = vf.flight_id 
                    """

        rows_to_insert = db_conn.execute(count_req).fetchone()[0]

        if rows_to_insert == 0:
            logger.info("fact_flight : No new line to insert")
            return 0

        logger.info(f"fact_flight : {rows_to_insert} new flights to insert")

        # Constructing the insertion request

        insert_req = """
                     INSERT INTO vayora_dw.fact_flight (fact_flight_bk, 
                                                  fact_flight_distance, 
                                                  fact_flight_airtime,
                                                  fact_flight_pilot,
                                                  fact_flight_takeoff,
                                                  fact_flight_weather,
                                                  fact_flight_start_date,
                                                  fact_flight_start_time)
                     SELECT
                         
                         vf.flight_id AS fact_flight_bk,

                         vf.flight_distance AS fact_flight_distance,
                         vf.flight_airtime AS fact_flight_airtime,

                         dp.dim_pilot_sk AS fact_flight_pilot,

                         dt.dim_takeoff_sk AS fact_flight_takeoff,

                         dw.dim_weather_sk AS fact_flight_weather,

                         -- FK to dim_date (format in YYYYMMDD)
                         CAST(strftime(vf.flight_starttime, '%Y%m%d') AS INTEGER) AS fact_flight_start_date,

                         -- FK to dim_time (format in HHMM)
                         (EXTRACT(HOUR FROM vf.flight_starttime) * 100 +
                          EXTRACT(MINUTE FROM vf.flight_starttime))::INTEGER AS fact_flight_start_time

                     FROM vayora.flight vf
                         
                     -- Excluding existing flights
                     ANTI JOIN vayora_dw.fact_flight ff ON ff.fact_flight_bk = vf.flight_id
                         
                     -- JOIN with dim_pilot 
                     INNER JOIN vayora.pilot p ON vf.flight_pilot_id = p.pilot_id
                     INNER JOIN vayora_dw.dim_pilot dp ON p.pilot_number = dp.dim_pilot_bk

                     -- JOIN with dim_takeoff
                     INNER JOIN vayora.takeoff vt ON vt.takeoff_id = vf.flight_takeoff_id
                     INNER JOIN vayora_dw.dim_takeoff dt ON vt.takeoff_name = dt.dim_takeoff_name

                     -- JOIN with dim_weather
                     INNER JOIN weather.weather_historic fw ON fw.weather_date = vf.flight_starttime AND fw.weather_place = vt.takeoff_name
                     INNER JOIN vayora_dw.dim_weather dw ON fw.weather_id = dw.dim_weather_bk

                     -- Check if flight date in dim_date   
                     WHERE CAST(strftime(vf.flight_starttime, '%Y%m%d') AS INTEGER) IN (SELECT date_key FROM vayora_dw.dim_date)
                    
                     -- Check if flight time in dim_time 
                     AND (EXTRACT(HOUR FROM vf.flight_starttime) * 100 + EXTRACT(MINUTE FROM vf.flight_starttime))::INTEGER IN (SELECT time_key FROM vayora_dw.dim_time)
                    """

        # Execution of the insertion request

        db_conn.execute("BEGIN TRANSACTION")

        try:
            db_conn.execute(insert_req)
            db_conn.commit()
            rows_inserted = rows_to_insert - db_conn.execute(count_req).fetchone()[0]
            elapsed = (dt.now() - start_time).total_seconds()

            logger.info(
                f"fact_flight : {rows_inserted} flights inserted successfully !"
                f"(duration: {elapsed:.2f}s)"
            )

            # check rejected flights
            get_rejected_flights(db_conn)

            # fact_flight post insertion validation
            validate_fact_flight(db_conn)

            return rows_inserted

        except Exception as e:
            db_conn.rollback()
            logger.error(f"fact_flight : Insertion failed - {e}")
            raise

    except Exception as e:
        logger.error(f"fact_flight : Critical Error - {e}")
        return -1


def validate_fact_flight(db_conn):
    """

    Check :
    1. Referential integrity with all dimensions
    2. Consistency of metrics (distance > 0, airtime > 0)
    3. Absence of duplicates
    """
    logger.info("=" * 70)
    logger.info("Validation of fact_flight")
    logger.info("=" * 70)

    try:
        # global statistics
        stats = db_conn.execute("""
                                SELECT COUNT(*)                            AS total_flights,
                                       COUNT(DISTINCT fact_flight_pilot)   AS distinct_pilots,
                                       COUNT(DISTINCT fact_flight_takeoff) AS distinct_takeoffs,
                                       COUNT(DISTINCT fact_flight_weather) AS distinct_weather,
                                       MIN(fact_flight_distance)           AS min_distance,
                                       MAX(fact_flight_distance)           AS max_distance,
                                       AVG(fact_flight_distance) ::INTEGER AS avg_distance
                                FROM vayora_dw.fact_flight
                                """).fetchone()

        logger.info(f"Total flights        : {stats[0]:,}")
        logger.info(f"Distinct pilots      : {stats[1]:,}")
        logger.info(f"Distinct takeoff     : {stats[2]:,}")
        logger.info(f"Weather conditions   : {stats[3]:,}")
        logger.info(f"Distance min/max/avg : {stats[4]:,} / {stats[5]:,} / {stats[6]:,} km")

        # Checking referential integrity
        unknown_pilots = db_conn.execute("""
                                        SELECT COUNT(*)
                                        FROM vayora_dw.fact_flight ff
                                        LEFT JOIN vayora_dw.dim_pilot dp ON ff.fact_flight_pilot = dp.dim_pilot_bk
                                        WHERE dp.dim_pilot_bk IS NULL
                                        """).fetchone()[0]

        if unknown_pilots > 0:
            logger.warning(f"{unknown_pilots} flights with unknown pilot !")  # not supposed to happen !!!
        else:
            logger.info("dim_pilot integrity : OK")

        unknown_takeoffs = db_conn.execute("""
                                          SELECT COUNT(*)
                                          FROM vayora_dw.fact_flight ff
                                          LEFT JOIN vayora_dw.dim_takeoff dt ON ff.fact_flight_takeoff = dt.dim_takeoff_sk
                                          WHERE dt.dim_takeoff_sk IS NULL
                                          """).fetchone()[0]

        if unknown_takeoffs > 0:
            logger.warning(f"{unknown_takeoffs} flights with unknown takeoffs !") # not supposed to happen !!!
        else:
            logger.info("dim_takeoff integrity : OK")

        unknown_weather = db_conn.execute("""
                                         SELECT COUNT(*)
                                         FROM vayora_dw.fact_flight ff
                                         LEFT JOIN vayora_dw.dim_weather dw ON ff.fact_flight_weather = dw.dim_weather_sk
                                         WHERE dw.dim_weather_sk IS NULL
                                         """).fetchone()[0]

        if unknown_weather > 0:
            logger.warning(f"{unknown_weather} flights with unknown weather !")
        else:
            logger.info("dim_weather integrity : OK")

        # Check metrics
        invalid_distances = db_conn.execute("""
                                            SELECT COUNT(*)
                                            FROM vayora_dw.fact_flight
                                            WHERE fact_flight_distance <= 0
                                            """).fetchone()[0]

        if invalid_distances > 0:
            logger.warning(f"{invalid_distances} flight with distance <= 0 !")
        else:
            logger.info("Distances : OK")

        # Check duplicates on business key
        duplicates = db_conn.execute("""
                                     SELECT COUNT(*)
                                     FROM (SELECT fact_flight_bk, COUNT(*) as cnt
                                           FROM vayora_dw.fact_flight
                                           GROUP BY fact_flight_bk
                                           HAVING COUNT(*) > 1) AS subq
                                     """).fetchone()[0]

        if duplicates > 0:
            logger.warning(f"{duplicates} business keys duplicates !")
        else:
            logger.info("fact_flight_bk unicity : OK")

        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"Error while validate : {e}")


def get_rejected_flights(db_conn):
    """
    Identify flights that they can't be loaded


    :return: a dictionary with the number of rejected flights in value and the reason in the key
    """
    logger.info("=" * 70)
    logger.info("Rejected Flights Analyses")
    logger.info("=" * 70)

    try:
        # Flights with unknown pilot
        missing_pilots = db_conn.execute("""
                                         SELECT count(*), count(distinct(vp.pilot_number))                                                
                                         FROM vayora.flight vf
                                         INNER JOIN vayora.pilot vp ON vp.pilot_id = vf.flight_pilot_id
                                         LEFT JOIN vayora_dw.dim_pilot dp ON vp.pilot_number = dp.dim_pilot_bk
                                         WHERE dp.dim_pilot_bk IS NULL AND NOT EXISTS (SELECT 1
                                                                                       FROM vayora_dw.fact_flight ff
                                                                                       WHERE ff.fact_flight_bk = vf.flight_id)
                                         """).fetchone()

        # Flights with unknown takeoff
        missing_takeoffs = db_conn.execute("""
                                           SELECT count(*), count(distinct(vt.takeoff_name))
                                           FROM vayora.flight vf
                                           INNER JOIN vayora.takeoff vt ON vf.flight_takeoff_id = vt.takeoff_id
                                           LEFT JOIN vayora_dw.dim_takeoff dt ON vt.takeoff_name = dt.dim_takeoff_name
                                           WHERE dt.dim_takeoff_sk IS NULL AND NOT EXISTS (SELECT 1
                                                                                           FROM vayora_dw.fact_flight ff
                                                                                           WHERE ff.fact_flight_bk = vf.flight_id)
                                           """).fetchone()

        # Flights with unknown weather
        missing_weather = db_conn.execute("""SELECT COUNT(*) 
                                             FROM vayora.flight vf 
                                             INNER JOIN vayora.takeoff vt ON vf.flight_takeoff_id = vt.takeoff_id 
                                             ANTI JOIN weather.weather_historic fw ON fw.weather_date = vf.flight_starttime AND fw.weather_place = vt.takeoff_name 
                                          """).fetchone()[0]

        logger.info(f"Flights rejected - Pilot unknown     : number of lines rejected : {missing_pilots[0]}   - number of distinct pilots  : {missing_pilots[1]}")
        logger.info(f"Flights rejected - Takeoff unknown   : number of lines rejected : {missing_takeoffs[0]} - number of distinct takeoff : {missing_takeoffs[1]}")
        logger.info(f"Flights rejected - Weather unknown   : {missing_weather}")

        total_rejected = missing_pilots[0] + missing_takeoffs[0] + missing_weather

        if total_rejected > 0:
            logger.warning(f"TOTAL Flights rejected : {total_rejected}")
            logger.warning("Please load the missing dimensions first")
        else:
            logger.info("No rejected flights")

        logger.info("=" * 70)

        return {
            'missing_pilots': missing_pilots,
            'missing_takeoffs': missing_takeoffs,
            'missing_weather': missing_weather
        }

    except Exception as e:
        logger.error(f"Error while analysing rejects : {e}")
        return None
