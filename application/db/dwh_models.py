from application.extensions import db

# Mostly generated with sqlacodegen --> pip install sqlacodegen --> sqlacodegen postgresql://user:password@localhost:5432/db_name --outfile models.py       

class DimDate(db.Model):
    __tablename__ = 'dim_date'
    __bind_key__ = "dw"

    date_key = db.Column(db.Integer, primary_key=True)
    full_date = db.Column(db.Date, nullable=False)
    day_number = db.Column(db.Integer)
    day_name = db.Column(db.String(10))
    day_of_week = db.Column(db.Integer)
    day_of_year = db.Column(db.Integer)
    week_number = db.Column(db.Integer)
    month_number = db.Column(db.Integer)
    month_name = db.Column(db.String(15))
    quarter_number = db.Column(db.Integer)
    year_number = db.Column(db.Integer)
    is_weekend = db.Column(db.Boolean)
    season = db.Column(db.String(10))
    is_holiday_fwb = db.Column(db.Boolean)
    is_holiday_vl = db.Column(db.Boolean)


class DimPilot(db.Model):
    __tablename__ = 'dim_pilot'
    __bind_key__ = "dw"
    __table_args__ = (
        db.UniqueConstraint('dim_pilot_bk', name='dim_pilot_dim_pilot_bk_key'),
    )

    dim_pilot_sk = db.Column(db.Integer, primary_key=True)
    dim_pilot_bk = db.Column(db.Integer, nullable=False)
    dim_pilot_maxdistance = db.Column(db.Integer)


class DimTakeoff(db.Model):
    __tablename__ = 'dim_takeoff'
    __bind_key__ = "dw"
    __table_args__ = (
        db.UniqueConstraint('dim_takeoff_bk', name='dim_takeoff_dim_takeoff_bk_key'),
    )

    dim_takeoff_sk = db.Column(db.Integer, primary_key=True)
    dim_takeoff_bk = db.Column(db.Integer, nullable=False)
    dim_takeoff_name = db.Column(db.String(100))


class DimTime(db.Model):
    __tablename__ = 'dim_time'
    __bind_key__ = "dw"

    time_key = db.Column(db.Integer, primary_key=True)
    full_time = db.Column(db.Time, nullable=False)
    hour_number = db.Column(db.Integer)
    minute_number = db.Column(db.Integer)
    period_of_day = db.Column(db.String(20))


class DimWeather(db.Model):
    __tablename__ = 'dim_weather'
    __bind_key__ = "dw"
    __table_args__ = (
        db.UniqueConstraint('dim_weather_bk', name='dim_weather_dim_weather_bk_key'),
    )

    dim_weather_sk = db.Column(db.Integer, primary_key=True)
    dim_weather_bk = db.Column(db.Integer, nullable=False)
    temperature_2m = db.Column(db.Numeric(6, 2))
    relative_humidity_2m = db.Column(db.Numeric(6, 2))
    dew_point_2m = db.Column(db.Numeric(6, 2))
    precipitation_probability = db.Column(db.Numeric(6, 2))
    precipitation = db.Column(db.Numeric(6, 2))
    rain = db.Column(db.Numeric(6, 2))
    showers = db.Column(db.Numeric(6, 2))
    snowfall = db.Column(db.Numeric(6, 2))
    pressure_msl = db.Column(db.Numeric(6, 2))
    surface_pressure = db.Column(db.Numeric(6, 2))
    cloud_cover = db.Column(db.Numeric(6, 2))
    cloud_cover_low = db.Column(db.Numeric(6, 2))
    cloud_cover_mid = db.Column(db.Numeric(6, 2))
    cloud_cover_high = db.Column(db.Numeric(6, 2))
    evapotranspiration = db.Column(db.Numeric(6, 2))
    wind_speed_10m = db.Column(db.Numeric(6, 2))
    wind_speed_80m = db.Column(db.Numeric(6, 2))
    wind_speed_120m = db.Column(db.Numeric(6, 2))
    wind_speed_180m = db.Column(db.Numeric(6, 2))
    wind_direction_10m = db.Column(db.Numeric(6, 2))
    wind_direction_80m = db.Column(db.Numeric(6, 2))
    wind_direction_120m = db.Column(db.Numeric(6, 2))
    wind_direction_180m = db.Column(db.Numeric(6, 2))
    wind_gusts_10m = db.Column(db.Numeric(6, 2))
    temperature_80m = db.Column(db.Numeric(6, 2))
    temperature_120m = db.Column(db.Numeric(6, 2))
    temperature_180m = db.Column(db.Numeric(6, 2))
    soil_moisture_1_to_3cm = db.Column(db.Numeric(6, 2))
    soil_moisture_9_to_27cm = db.Column(db.Numeric(6, 2))
    temperature_950hpa = db.Column(db.Numeric(6, 2))
    temperature_925hpa = db.Column(db.Numeric(6, 2))
    temperature_900hpa = db.Column(db.Numeric(6, 2))
    temperature_850hpa = db.Column(db.Numeric(6, 2))
    temperature_800hpa = db.Column(db.Numeric(6, 2))
    relative_humidity_950hpa = db.Column(db.Numeric(6, 2))
    relative_humidity_925hpa = db.Column(db.Numeric(6, 2))
    relative_humidity_900hpa = db.Column(db.Numeric(6, 2))
    relative_humidity_850hpa = db.Column(db.Numeric(6, 2))
    relative_humidity_800hpa = db.Column(db.Numeric(6, 2))
    cloud_cover_950hpa = db.Column(db.Numeric(6, 2))
    cloud_cover_925hpa = db.Column(db.Numeric(6, 2))
    cloud_cover_900hpa = db.Column(db.Numeric(6, 2))
    cloud_cover_850hpa = db.Column(db.Numeric(6, 2))
    cloud_cover_800hpa = db.Column(db.Numeric(6, 2))
    wind_speed_950hpa = db.Column(db.Numeric(6, 2))
    wind_speed_925hpa = db.Column(db.Numeric(6, 2))
    wind_speed_900hpa = db.Column(db.Numeric(6, 2))
    wind_speed_850hpa = db.Column(db.Numeric(6, 2))
    wind_speed_800hpa = db.Column(db.Numeric(6, 2))
    wind_direction_950hpa = db.Column(db.Numeric(5, 2))
    wind_direction_925hpa = db.Column(db.Numeric(6, 2))
    wind_direction_900hpa = db.Column(db.Numeric(6, 2))
    wind_direction_850hpa = db.Column(db.Numeric(6, 2))
    wind_direction_800hpa = db.Column(db.Numeric(6, 2))
    geopotential_height_950hpa = db.Column(db.Numeric(6, 2))
    geopotential_height_925hpa = db.Column(db.Numeric(6, 2))
    geopotential_height_900hpa = db.Column(db.Numeric(6, 2))
    geopotential_height_850hpa = db.Column(db.Numeric(6, 2))
    geopotential_height_800hpa = db.Column(db.Numeric(6, 2))


class FactFly(db.Model):
    __tablename__ = 'fact_fly'
    __bind_key__ = "dw"
    __table_args__ = (
        db.ForeignKeyConstraint(['fact_fly_pilot'], ['dim_pilot.dim_pilot_sk'], name='fact_fly_fact_fly_pilot_fkey'),
        db.ForeignKeyConstraint(['fact_fly_start_date'], ['dim_date.date_key'], name='fact_fly_fact_fly_start_date_fkey'),
        db.ForeignKeyConstraint(['fact_fly_start_time'], ['dim_time.time_key'], name='fact_fly_fact_fly_start_time_fkey'),
        db.ForeignKeyConstraint(['fact_fly_takeoff'], ['dim_takeoff.dim_takeoff_sk'], name='fact_fly_fact_fly_takeoff_fkey'),
        db.ForeignKeyConstraint(['fact_fly_weather'], ['dim_weather.dim_weather_sk'], name='fact_fly_fact_fly_weather_fkey'),
        db.UniqueConstraint('fact_fly_bk', name='fact_fly_fact_fly_bk_key')
    )

    fact_fly_sk = db.Column(db.Integer, primary_key=True)
    fact_fly_bk = db.Column(db.Integer, nullable=False)
    fact_fly_distance = db.Column(db.Integer, nullable=False)
    fact_fly_airtime = db.Column(db.Time, nullable=False)
    fact_fly_pilot = db.Column(db.Integer)
    fact_fly_takeoff = db.Column(db.Integer)
    fact_fly_weather = db.Column(db.Integer)
    fact_fly_start_date = db.Column(db.Integer)
    fact_fly_start_time = db.Column(db.Integer)

    dim_pilot = db.relationship('DimPilot', backref='fact_fly')
    dim_date = db.relationship('DimDate', backref='fact_fly')
    dim_time = db.relationship('DimTime', backref='fact_fly')
    dim_takeoff = db.relationship('DimTakeoff', backref='fact_fly')
    dim_weather = db.relationship('DimWeather', backref='fact_fly')
