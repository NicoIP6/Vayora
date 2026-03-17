from shared.database_file.extensions import db
from sqlalchemy.dialects.postgresql import TIMESTAMP


class Historicweather(db.Model):
    __tablename__ = 'weather_historic'
    __bind_key__ = "weather"


    weather_id = db.Column(db.Integer, primary_key=True)
    weather_date = db.Column(TIMESTAMP(timezone=False, precision=0), nullable=False)
    temperature_2m = db.Column(db.Numeric(6, 2))
    boundary_layer_height = db.Column(db.Integer)
    lifted_index = db.Column(db.Numeric(4, 2)) # atmospheric instability measurement in C°. 'LI > 0' = weak storm risk even null LI < -6 = huge instability and violent storm risk
    convective_inhibition = db.Column(db.Integer)
    cloud_cover = db.Column(db.Numeric(6, 2))
    cloud_cover_low = db.Column(db.Numeric(6, 2))
    cloud_cover_mid = db.Column(db.Numeric(6, 2))
    cloud_cover_high = db.Column(db.Numeric(6, 2))
    wind_direction_120m = db.Column(db.Numeric(6, 2))
    wind_speed_120m = db.Column(db.Numeric(6, 2))
    precipitation = db.Column(db.Numeric(6, 2))
    precipitation_probability = db.Column(db.Numeric(6, 2))
    temperature_120m = db.Column(db.Numeric(6, 2))
    pressure_msl = db.Column(db.Numeric(6, 2))
    surface_pressure = db.Column(db.Numeric(6, 2))
    cape = db.Column(db.Integer)
    temperature_950hpa = db.Column(db.Numeric(6, 2))
    temperature_700hpa = db.Column(db.Numeric(6, 2))
    relative_humidity_950hpa = db.Column(db.Numeric(6, 2))
    relative_humidity_700hpa = db.Column(db.Numeric(6, 2))
    wind_speed_950hpa = db.Column(db.Numeric(6, 2))
    wind_speed_850hpa = db.Column(db.Numeric(6, 2))
    wind_speed_800hpa = db.Column(db.Numeric(6, 2))
    wind_speed_700hpa = db.Column(db.Numeric(6, 2))
    wind_direction_950hpa = db.Column(db.Numeric(6, 2))
    wind_direction_850hpa = db.Column(db.Numeric(6, 2))
    wind_direction_800hpa = db.Column(db.Numeric(6, 2))
    wind_direction_700hpa = db.Column(db.Numeric(6, 2))
    wind_direction_600hpa = db.Column(db.Numeric(6, 2))
    geopotential_height_950hpa = db.Column(db.Integer)
    geopotential_height_600hpa = db.Column(db.Integer)
    temperature_600hpa = db.Column(db.Numeric(6, 2))
    relative_humidity_600hpa = db.Column(db.Numeric(6, 2))
    wind_speed_600hpa = db.Column(db.Numeric(6, 2))
    geopotential_height_700hpa = db.Column(db.Integer)
    weather_place = db.Column(db.String(200), nullable=False)