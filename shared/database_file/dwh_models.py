from shared.database_file.extensions import db

# Mostly generated with sqlacodegen --> pip install sqlacodegen --> sqlacodegen postgresql://user:password@localhost:5432/db_name --outfile models.py       

class DimDate(db.Model):
    __tablename__ = 'dim_date'
    __bind_key__ = "vayora_dw"

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
    __bind_key__ = "vayora_dw"
    __table_args__ = (
        db.UniqueConstraint('dim_pilot_bk', name='dim_pilot_dim_pilot_bk_key'),
    )

    dim_pilot_sk = db.Column(db.Integer, primary_key=True)
    dim_pilot_bk = db.Column(db.Integer, nullable=False)
    dim_pilot_maxdistance = db.Column(db.Integer)


class DimTakeoff(db.Model):
    __tablename__ = 'dim_takeoff'
    __bind_key__ = "vayora_dw"
    __table_args__ = (
        db.UniqueConstraint('dim_takeoff_bk', name='dim_takeoff_dim_takeoff_bk_key'),
    )

    dim_takeoff_sk = db.Column(db.Integer, primary_key=True)
    dim_takeoff_bk = db.Column(db.Integer, nullable=False)
    dim_takeoff_name = db.Column(db.String(100))


class DimTime(db.Model):
    __tablename__ = 'dim_time'
    __bind_key__ = "vayora_dw"

    time_key = db.Column(db.Integer, primary_key=True)
    full_time = db.Column(db.Time, nullable=False)
    hour_number = db.Column(db.Integer)
    minute_number = db.Column(db.Integer)
    period_of_day = db.Column(db.String(20))


class DimWeather(db.Model):
    __tablename__ = 'dim_weather'
    __bind_key__ = "vayora_dw"
    __table_args__ = (
        db.UniqueConstraint('dim_weather_bk', name='dim_weather_dim_weather_bk_key'),
    )

    dim_weather_sk = db.Column(db.Integer, primary_key=True)
    dim_weather_bk = db.Column(db.Integer, nullable=False)
    temperature_2m = db.Column(db.Numeric(6, 2))
    boundary_layer_height = db.Column(db.Integer)
    lifted_index = db.Column(db.Numeric(4, 2))  # atmospheric instability measurement in C°. 'LI > 0' = weak storm risk even null LI < -6 = huge instability and violent storm risk
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


class FactFlight(db.Model):
    __tablename__ = 'fact_flight'
    __bind_key__ = "vayora_dw"
    __table_args__ = (
        db.ForeignKeyConstraint(['fact_flight_pilot'], ['dim_pilot.dim_pilot_sk'], name='fact_flight_fact_flight_pilot_fkey'),
        db.ForeignKeyConstraint(['fact_flight_start_date'], ['dim_date.date_key'], name='fact_flight_fact_flight_start_date_fkey'),
        db.ForeignKeyConstraint(['fact_flight_start_time'], ['dim_time.time_key'], name='fact_flight_fact_flight_start_time_fkey'),
        db.ForeignKeyConstraint(['fact_flight_takeoff'], ['dim_takeoff.dim_takeoff_sk'], name='fact_flight_fact_flight_takeoff_fkey'),
        db.ForeignKeyConstraint(['fact_flight_weather'], ['dim_weather.dim_weather_sk'], name='fact_flight_fact_flight_weather_fkey'),
        db.UniqueConstraint('fact_flight_bk', name='fact_flight_fact_flight_bk_key')
    )

    fact_flight_sk = db.Column(db.Integer, primary_key=True)
    fact_flight_bk = db.Column(db.Integer, nullable=False)
    fact_flight_distance = db.Column(db.Integer, nullable=False)
    fact_flight_airtime = db.Column(db.Time, nullable=False)
    fact_flight_pilot = db.Column(db.Integer)
    fact_flight_takeoff = db.Column(db.Integer)
    fact_flight_weather = db.Column(db.Integer)
    fact_flight_start_date = db.Column(db.Integer)
    fact_flight_start_time = db.Column(db.Integer)

    dim_pilot = db.relationship('DimPilot', backref='fact_flight')
    dim_date = db.relationship('DimDate', backref='fact_flight')
    dim_time = db.relationship('DimTime', backref='fact_flight')
    dim_takeoff = db.relationship('DimTakeoff', backref='fact_flight')
    dim_weather = db.relationship('DimWeather', backref='fact_flight')
