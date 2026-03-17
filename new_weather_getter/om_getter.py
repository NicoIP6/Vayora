import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import json
import time
from pathlib import Path

base_dir = Path(__file__).resolve().parent
file_path = base_dir / "final_takeoff_geoCor.json"
with open(file_path, "r") as f:
    takeoff_file = json.load(f)

for i, j in takeoff_file.items():
    takeoff_file[i] = [round(j[0], 2), round(j[1], 2), j[2]]

for key, value in takeoff_file.items():
    if value[2] != 'Plaine':
        with requests_cache.CachedSession('.cache', expire_after=3600) as cache_session:
            retry_session = retry(cache_session, retries=5, backoff_factor=0.5)
            openmeteo = openmeteo_requests.Client(session=retry_session)
            print(f"Extract {key} weather\n")
            lat = value[0]
            long = value[1]
            # Set up the Open-Meteo API client with cache and retry on error


            print("OM connection ok")
            # Make sure all required weather variables are listed here
            # The order of variables in hourly or daily is important to assign them correctly below
            url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": long,
                "start_date": "2022-01-01",
                "end_date": "2024-12-31",
                "hourly": ["temperature_2m", "boundary_layer_height", "lifted_index", "convective_inhibition", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "wind_direction_120m", "wind_speed_120m", "precipitation", "precipitation_probability", "temperature_120m", "pressure_msl", "surface_pressure", "cape", "temperature_950hPa", "temperature_700hPa", "relative_humidity_950hPa", "relative_humidity_700hPa", "wind_speed_950hPa", "wind_speed_850hPa", "wind_speed_800hPa", "wind_speed_700hPa", "wind_direction_950hPa", "wind_direction_850hPa", "wind_direction_800hPa", "wind_direction_700hPa", "wind_direction_600hPa", "geopotential_height_950hPa", "geopotential_height_600hPa", "temperature_600hPa", "relative_humidity_600hPa", "wind_speed_600hPa", "geopotential_height_700hPa"],
            }
            responses = openmeteo.weather_api(url, params=params)
            time.sleep(1)

            # Process first location. Add a for-loop for multiple locations or weather models
            response = responses[0]
            print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
            print(f"Elevation: {response.Elevation()} m asl")
            print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

            # Process hourly data. The order of variables needs to be the same as requested.
            hourly = response.Hourly()
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            hourly_boundary_layer_height = hourly.Variables(1).ValuesAsNumpy()
            hourly_lifted_index = hourly.Variables(2).ValuesAsNumpy()
            hourly_convective_inhibition = hourly.Variables(3).ValuesAsNumpy()
            hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()
            hourly_cloud_cover_low = hourly.Variables(5).ValuesAsNumpy()
            hourly_cloud_cover_mid = hourly.Variables(6).ValuesAsNumpy()
            hourly_cloud_cover_high = hourly.Variables(7).ValuesAsNumpy()
            hourly_wind_direction_120m = hourly.Variables(8).ValuesAsNumpy()
            hourly_wind_speed_120m = hourly.Variables(9).ValuesAsNumpy()
            hourly_precipitation = hourly.Variables(10).ValuesAsNumpy()
            hourly_precipitation_probability = hourly.Variables(11).ValuesAsNumpy()
            hourly_temperature_120m = hourly.Variables(12).ValuesAsNumpy()
            hourly_pressure_msl = hourly.Variables(13).ValuesAsNumpy()
            hourly_surface_pressure = hourly.Variables(14).ValuesAsNumpy()
            hourly_cape = hourly.Variables(15).ValuesAsNumpy()
            hourly_temperature_950hPa = hourly.Variables(16).ValuesAsNumpy()
            hourly_temperature_700hPa = hourly.Variables(17).ValuesAsNumpy()
            hourly_relative_humidity_950hPa = hourly.Variables(18).ValuesAsNumpy()
            hourly_relative_humidity_700hPa = hourly.Variables(19).ValuesAsNumpy()
            hourly_wind_speed_950hPa = hourly.Variables(20).ValuesAsNumpy()
            hourly_wind_speed_850hPa = hourly.Variables(21).ValuesAsNumpy()
            hourly_wind_speed_800hPa = hourly.Variables(22).ValuesAsNumpy()
            hourly_wind_speed_700hPa = hourly.Variables(23).ValuesAsNumpy()
            hourly_wind_direction_950hPa = hourly.Variables(24).ValuesAsNumpy()
            hourly_wind_direction_850hPa = hourly.Variables(25).ValuesAsNumpy()
            hourly_wind_direction_800hPa = hourly.Variables(26).ValuesAsNumpy()
            hourly_wind_direction_700hPa = hourly.Variables(27).ValuesAsNumpy()
            hourly_wind_direction_600hPa = hourly.Variables(28).ValuesAsNumpy()
            hourly_geopotential_height_950hPa = hourly.Variables(29).ValuesAsNumpy()
            hourly_geopotential_height_600hPa = hourly.Variables(30).ValuesAsNumpy()
            hourly_temperature_600hPa = hourly.Variables(31).ValuesAsNumpy()
            hourly_relative_humidity_600hPa = hourly.Variables(32).ValuesAsNumpy()
            hourly_wind_speed_600hPa = hourly.Variables(33).ValuesAsNumpy()
            hourly_geopotential_height_700hPa = hourly.Variables(34).ValuesAsNumpy()
            print("Datas exctracted - building dataframe")
            time.sleep(3)
            hourly_data = {"date": pd.date_range(
                start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
                end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
                freq = pd.Timedelta(seconds = hourly.Interval()),
                inclusive = "left"
            )}

            hourly_data["temperature_2m"] = hourly_temperature_2m
            hourly_data["boundary_layer_height"] = hourly_boundary_layer_height
            hourly_data["lifted_index"] = hourly_lifted_index
            hourly_data["convective_inhibition"] = hourly_convective_inhibition
            hourly_data["cloud_cover"] = hourly_cloud_cover
            hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
            hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
            hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
            hourly_data["wind_direction_120m"] = hourly_wind_direction_120m
            hourly_data["wind_speed_120m"] = hourly_wind_speed_120m
            hourly_data["precipitation"] = hourly_precipitation
            hourly_data["precipitation_probability"] = hourly_precipitation_probability
            hourly_data["temperature_120m"] = hourly_temperature_120m
            hourly_data["pressure_msl"] = hourly_pressure_msl
            hourly_data["surface_pressure"] = hourly_surface_pressure
            hourly_data["cape"] = hourly_cape
            hourly_data["temperature_950hPa"] = hourly_temperature_950hPa
            hourly_data["temperature_700hPa"] = hourly_temperature_700hPa
            hourly_data["relative_humidity_950hPa"] = hourly_relative_humidity_950hPa
            hourly_data["relative_humidity_700hPa"] = hourly_relative_humidity_700hPa
            hourly_data["wind_speed_950hPa"] = hourly_wind_speed_950hPa
            hourly_data["wind_speed_850hPa"] = hourly_wind_speed_850hPa
            hourly_data["wind_speed_800hPa"] = hourly_wind_speed_800hPa
            hourly_data["wind_speed_700hPa"] = hourly_wind_speed_700hPa
            hourly_data["wind_direction_950hPa"] = hourly_wind_direction_950hPa
            hourly_data["wind_direction_850hPa"] = hourly_wind_direction_850hPa
            hourly_data["wind_direction_800hPa"] = hourly_wind_direction_800hPa
            hourly_data["wind_direction_700hPa"] = hourly_wind_direction_700hPa
            hourly_data["wind_direction_600hPa"] = hourly_wind_direction_600hPa
            hourly_data["geopotential_height_950hPa"] = hourly_geopotential_height_950hPa
            hourly_data["geopotential_height_600hPa"] = hourly_geopotential_height_600hPa
            hourly_data["temperature_600hPa"] = hourly_temperature_600hPa
            hourly_data["relative_humidity_600hPa"] = hourly_relative_humidity_600hPa
            hourly_data["wind_speed_600hPa"] = hourly_wind_speed_600hPa
            hourly_data["geopotential_height_700hPa"] = hourly_geopotential_height_700hPa

            hourly_dataframe = pd.DataFrame(data = hourly_data)
            print(f"{key} - dataframe build\n")

            hourly_dataframe.to_csv(f"{key}.csv", index=False, encoding='utf-8')


        print("\nSleeping\n")
        time.sleep(250)
        cache_session.cache.clear()


