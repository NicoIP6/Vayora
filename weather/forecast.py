import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from weather.fill_weather import insert_weather
from shared.database_file.set_up import Setup
from datetime import datetime as dt


def get_forecast(lat, lng, tkf_name):


    # Set up the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lng,
        "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "precipitation_probability",
                   "precipitation", "rain", "showers", "snowfall", "pressure_msl", "surface_pressure", "cloud_cover",
                   "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "evapotranspiration", "wind_speed_10m",
                   "wind_speed_80m", "wind_speed_180m", "wind_speed_120m", "wind_direction_10m", "wind_direction_80m",
                   "wind_direction_120m", "wind_direction_180m", "wind_gusts_10m", "temperature_80m",
                   "temperature_120m", "temperature_180m", "soil_moisture_1_to_3cm", "soil_moisture_9_to_27cm",
                   "temperature_950hPa", "temperature_925hPa", "temperature_900hPa", "temperature_850hPa",
                   "temperature_800hPa", "relative_humidity_950hPa", "relative_humidity_925hPa",
                   "relative_humidity_900hPa", "relative_humidity_850hPa", "relative_humidity_800hPa",
                   "cloud_cover_950hPa", "cloud_cover_925hPa", "cloud_cover_900hPa", "cloud_cover_850hPa",
                   "cloud_cover_800hPa", "wind_speed_950hPa", "wind_speed_925hPa", "wind_speed_900hPa",
                   "wind_speed_850hPa", "wind_speed_800hPa", "wind_direction_950hPa", "wind_direction_925hPa",
                   "wind_direction_900hPa", "wind_direction_850hPa", "wind_direction_800hPa",
                   "geopotential_height_950hPa", "geopotential_height_925hPa", "geopotential_height_900hPa",
                   "geopotential_height_850hPa", "geopotential_height_800hPa"],
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_dew_point_2m = hourly.Variables(2).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(3).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(4).ValuesAsNumpy()
    hourly_rain = hourly.Variables(5).ValuesAsNumpy()
    hourly_showers = hourly.Variables(6).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(7).ValuesAsNumpy()
    hourly_pressure_msl = hourly.Variables(8).ValuesAsNumpy()
    hourly_surface_pressure = hourly.Variables(9).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(10).ValuesAsNumpy()
    hourly_cloud_cover_low = hourly.Variables(11).ValuesAsNumpy()
    hourly_cloud_cover_mid = hourly.Variables(12).ValuesAsNumpy()
    hourly_cloud_cover_high = hourly.Variables(13).ValuesAsNumpy()
    hourly_evapotranspiration = hourly.Variables(14).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(15).ValuesAsNumpy()
    hourly_wind_speed_80m = hourly.Variables(16).ValuesAsNumpy()
    hourly_wind_speed_180m = hourly.Variables(17).ValuesAsNumpy()
    hourly_wind_speed_120m = hourly.Variables(18).ValuesAsNumpy()
    hourly_wind_direction_10m = hourly.Variables(19).ValuesAsNumpy()
    hourly_wind_direction_80m = hourly.Variables(20).ValuesAsNumpy()
    hourly_wind_direction_120m = hourly.Variables(21).ValuesAsNumpy()
    hourly_wind_direction_180m = hourly.Variables(22).ValuesAsNumpy()
    hourly_wind_gusts_10m = hourly.Variables(23).ValuesAsNumpy()
    hourly_temperature_80m = hourly.Variables(24).ValuesAsNumpy()
    hourly_temperature_120m = hourly.Variables(25).ValuesAsNumpy()
    hourly_temperature_180m = hourly.Variables(26).ValuesAsNumpy()
    hourly_soil_moisture_1_to_3cm = hourly.Variables(27).ValuesAsNumpy()
    hourly_soil_moisture_9_to_27cm = hourly.Variables(28).ValuesAsNumpy()
    hourly_temperature_950hPa = hourly.Variables(29).ValuesAsNumpy()
    hourly_temperature_925hPa = hourly.Variables(30).ValuesAsNumpy()
    hourly_temperature_900hPa = hourly.Variables(31).ValuesAsNumpy()
    hourly_temperature_850hPa = hourly.Variables(32).ValuesAsNumpy()
    hourly_temperature_800hPa = hourly.Variables(33).ValuesAsNumpy()
    hourly_relative_humidity_950hPa = hourly.Variables(34).ValuesAsNumpy()
    hourly_relative_humidity_925hPa = hourly.Variables(35).ValuesAsNumpy()
    hourly_relative_humidity_900hPa = hourly.Variables(36).ValuesAsNumpy()
    hourly_relative_humidity_850hPa = hourly.Variables(37).ValuesAsNumpy()
    hourly_relative_humidity_800hPa = hourly.Variables(38).ValuesAsNumpy()
    hourly_cloud_cover_950hPa = hourly.Variables(39).ValuesAsNumpy()
    hourly_cloud_cover_925hPa = hourly.Variables(40).ValuesAsNumpy()
    hourly_cloud_cover_900hPa = hourly.Variables(41).ValuesAsNumpy()
    hourly_cloud_cover_850hPa = hourly.Variables(42).ValuesAsNumpy()
    hourly_cloud_cover_800hPa = hourly.Variables(43).ValuesAsNumpy()
    hourly_wind_speed_950hPa = hourly.Variables(44).ValuesAsNumpy()
    hourly_wind_speed_925hPa = hourly.Variables(45).ValuesAsNumpy()
    hourly_wind_speed_900hPa = hourly.Variables(46).ValuesAsNumpy()
    hourly_wind_speed_850hPa = hourly.Variables(47).ValuesAsNumpy()
    hourly_wind_speed_800hPa = hourly.Variables(48).ValuesAsNumpy()
    hourly_wind_direction_950hPa = hourly.Variables(49).ValuesAsNumpy()
    hourly_wind_direction_925hPa = hourly.Variables(50).ValuesAsNumpy()
    hourly_wind_direction_900hPa = hourly.Variables(51).ValuesAsNumpy()
    hourly_wind_direction_850hPa = hourly.Variables(52).ValuesAsNumpy()
    hourly_wind_direction_800hPa = hourly.Variables(53).ValuesAsNumpy()
    hourly_geopotential_height_950hPa = hourly.Variables(54).ValuesAsNumpy()
    hourly_geopotential_height_925hPa = hourly.Variables(55).ValuesAsNumpy()
    hourly_geopotential_height_900hPa = hourly.Variables(56).ValuesAsNumpy()
    hourly_geopotential_height_850hPa = hourly.Variables(57).ValuesAsNumpy()
    hourly_geopotential_height_800hPa = hourly.Variables(58).ValuesAsNumpy()

    hourly_data = {"weather_date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}

    hourly_data["forecast_date"] = dt.now(tz=None).strftime("%Y-%m-%d %H:%M:%S")
    hourly_data["weather_place"] = tkf_name
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["dew_point_2m"] = hourly_dew_point_2m
    hourly_data["precipitation_probability"] = hourly_precipitation_probability
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["rain"] = hourly_rain
    hourly_data["showers"] = hourly_showers
    hourly_data["snowfall"] = hourly_snowfall
    hourly_data["pressure_msl"] = hourly_pressure_msl
    hourly_data["surface_pressure"] = hourly_surface_pressure
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
    hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
    hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
    hourly_data["evapotranspiration"] = hourly_evapotranspiration
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_speed_80m"] = hourly_wind_speed_80m
    hourly_data["wind_speed_180m"] = hourly_wind_speed_180m
    hourly_data["wind_speed_120m"] = hourly_wind_speed_120m
    hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
    hourly_data["wind_direction_80m"] = hourly_wind_direction_80m
    hourly_data["wind_direction_120m"] = hourly_wind_direction_120m
    hourly_data["wind_direction_180m"] = hourly_wind_direction_180m
    hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m
    hourly_data["temperature_80m"] = hourly_temperature_80m
    hourly_data["temperature_120m"] = hourly_temperature_120m
    hourly_data["temperature_180m"] = hourly_temperature_180m
    hourly_data["soil_moisture_1_to_3cm"] = hourly_soil_moisture_1_to_3cm
    hourly_data["soil_moisture_9_to_27cm"] = hourly_soil_moisture_9_to_27cm
    hourly_data["temperature_950hPa"] = hourly_temperature_950hPa
    hourly_data["temperature_925hPa"] = hourly_temperature_925hPa
    hourly_data["temperature_900hPa"] = hourly_temperature_900hPa
    hourly_data["temperature_850hPa"] = hourly_temperature_850hPa
    hourly_data["temperature_800hPa"] = hourly_temperature_800hPa
    hourly_data["relative_humidity_950hPa"] = hourly_relative_humidity_950hPa
    hourly_data["relative_humidity_925hPa"] = hourly_relative_humidity_925hPa
    hourly_data["relative_humidity_900hPa"] = hourly_relative_humidity_900hPa
    hourly_data["relative_humidity_850hPa"] = hourly_relative_humidity_850hPa
    hourly_data["relative_humidity_800hPa"] = hourly_relative_humidity_800hPa
    hourly_data["cloud_cover_950hPa"] = hourly_cloud_cover_950hPa
    hourly_data["cloud_cover_925hPa"] = hourly_cloud_cover_925hPa
    hourly_data["cloud_cover_900hPa"] = hourly_cloud_cover_900hPa
    hourly_data["cloud_cover_850hPa"] = hourly_cloud_cover_850hPa
    hourly_data["cloud_cover_800hPa"] = hourly_cloud_cover_800hPa
    hourly_data["wind_speed_950hPa"] = hourly_wind_speed_950hPa
    hourly_data["wind_speed_925hPa"] = hourly_wind_speed_925hPa
    hourly_data["wind_speed_900hPa"] = hourly_wind_speed_900hPa
    hourly_data["wind_speed_850hPa"] = hourly_wind_speed_850hPa
    hourly_data["wind_speed_800hPa"] = hourly_wind_speed_800hPa
    hourly_data["wind_direction_950hPa"] = hourly_wind_direction_950hPa
    hourly_data["wind_direction_925hPa"] = hourly_wind_direction_925hPa
    hourly_data["wind_direction_900hPa"] = hourly_wind_direction_900hPa
    hourly_data["wind_direction_850hPa"] = hourly_wind_direction_850hPa
    hourly_data["wind_direction_800hPa"] = hourly_wind_direction_800hPa
    hourly_data["geopotential_height_950hPa"] = hourly_geopotential_height_950hPa
    hourly_data["geopotential_height_925hPa"] = hourly_geopotential_height_925hPa
    hourly_data["geopotential_height_900hPa"] = hourly_geopotential_height_900hPa
    hourly_data["geopotential_height_850hPa"] = hourly_geopotential_height_850hPa
    hourly_data["geopotential_height_800hPa"] = hourly_geopotential_height_800hPa

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    print("\nHourly data\n", hourly_dataframe)

    return hourly_dataframe

if __name__ == "__main__":

    conn = Setup.get_duckdb_conn()
    takeoffs = conn.execute("""
                            SELECT tkf.takeoff_name, tkf.takeoff_latitude, tkf.takeoff_longitude 
                            FROM vayora.takeoff tkf
                            JOIN vayora.address ad ON ad.address_id = tkf.takeoff_address_id
                            JOIN vayora.country ctr ON ctr.country_id = ad.address_country_id
                            WHERE LOWER(ctr.country_code) = 'be'
                            OR tkf.takeoff_name IN ('fumay', 'revin', 'létanne', 'blanc nez', 'haulmé', 'equihen')
                            """).fetchall()
    for raw in takeoffs:
        forecast_df = get_forecast(raw[1], raw[2], raw[0])
        insert_weather('vayora', 'weather_forecast', forecast_df, conn)
