from application.db.dimensions_functions import fill_dim_pilot, fill_dim_weather, fill_dim_takeoff
from application.db.fact_table_functions import fill_fact_fly
from application.db.connexion_function import setup_duckdb

oltp_conn = ("vayora", 'postgresql://postgres:passwordfortest@localhost:5432/vayora_test')
stating_conn = ("forecast", 'postgresql://postgres:passwordfortest@localhost:5432/vayora_weather_staging')
dwh_conn = ("dwh", 'postgresql://postgres:passwordfortest@localhost:5432/vayora_dw')

postgres_conn = setup_duckdb(oltp_conn, stating_conn, dwh_conn)

fill_dim_pilot(postgres_conn)
fill_dim_takeoff(postgres_conn)
fill_dim_weather(postgres_conn)
result = fill_fact_fly(postgres_conn)

print(f"\n{'=' * 70}")
if result > 0:
    print(f"Successful loading : {result} flights inserted")
elif result == 0:
    print("No new flight inserted")
else:
    print("Loading failed")
print(f"{'=' * 70}\n")

