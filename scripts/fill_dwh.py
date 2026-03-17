from shared.database_file.dimensions_functions import fill_dim_pilot, fill_dim_weather, fill_dim_takeoff
from shared.database_file.fact_table_functions import fill_fact_flight
from shared.database_file.set_up import Setup
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logging"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "dwh.log"


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ],
    force=True
)

postgres_conn = Setup.get_duckdb_conn()

fill_dim_pilot(postgres_conn)
fill_dim_takeoff(postgres_conn)
fill_dim_weather(postgres_conn)
result = fill_fact_flight(postgres_conn)

print(f"\n{'=' * 70}")
if result > 0:
    print(f"Successful loading : {result} flights inserted")
elif result == 0:
    print("No new flight inserted")
else:
    print("Loading failed")
print(f"{'=' * 70}\n")

