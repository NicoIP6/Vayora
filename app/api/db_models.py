from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:passwordfortest@localhost:5432/vayora_test'

db = SQLAlchemy(app)
user_address = db.Table('user_address',
                        db.Column('users_id', db.Integer, db.ForeignKey('users.users_id')),
                        db.Column('address_id', db.Integer, db.ForeignKey('address.address_id'))
                        )

class Users(db.Model):
    __tablename__ = 'users'
    users_id = db.Column(db.Integer, primary_key=True)
    users_firstname = db.Column(db.String(150), nullable=False)
    users_lastname = db.Column(db.String(150), nullable=False)
    users_email = db.Column(db.String(250), nullable=False)
    users_phone = db.Column(db.String(20))
    users_birthday = db.Column(db.Date)
    users_address = db.relationship('Address', secondary=user_address, backref='users')

class Pilot(db.Model):
    pilot_id = db.Column(db.Integer, primary_key=True)
    pilot_license_number = db.Column(db.String(150), nullable=True)
    pilot_maxdistance = db.Column(db.Integer, nullable=True)

class Validator(db.Model):
    validator_id = db.Column(db.Integer, primary_key=True)
    validator_score = db.Column(db.Integer, nullable=True)


class Takeoff(db.Model):
    takeoff_id = db.Column(db.Integer, primary_key=True)
    takeoff_name = db.Column(db.String(150), nullable=False)
    takeoff_latitude = db.Column(db.Float, nullable=False)
    takeoff_longitude = db.Column(db.Float, nullable=False)
    takeoff_type = db.Column(db.String(150), nullable=True)
    takeoff_directionDegreeMin = db.Column(db.Integer, nullable=True)
    takeoff_directionDegreeMax = db.Column(db.Integer, nullable=True)
    takeoff_globalDirection = db.Column(db.String(150), nullable=True)
    takeoff_elevation = db.Column(db.Integer, nullable=True)
    takeoff_verticalDrop = db.Column(db.Integer, nullable=True)
    takeoff_difficulty = db.Column(db.String(30), nullable=True)
    takeoff_comment = db.Column(db.Text, nullable= True)
    takeoff_address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)
    takeoff_address = db.relationship('Address', backref='takeoffs')

class Flight(db.Model):
    flight_id = db.Column(db.Integer, primary_key=True)
    flight_startTime = db.Column(db.DateTime, nullable=False)
    flight_airTime = db.Column(db.Interval, nullable=False)
    flight_distance = db.Column(db.Integer, nullable=True)
    flight_maxHeight = db.Column(db.Integer, nullable=False)
    flight_landing = db.Column(db.String(250), nullable=True)
    flight_pilot_id = db.Column(db.Integer, db.ForeignKey('pilot.pilot_id'), nullable=False)
    flight_pilot = db.relationship('Pilot', backref='flights')
    flight_takeoff_id = db.Column(db.Integer, db.ForeignKey('takeoff.takeoff_id'))
    flight_takeoff = db.relationship('Takeoff', backref='flights')

class Country(db.Model):
    country_id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(150), nullable=False)
    country_code = db.Column(db.String(2), nullable=False)

class City(db.Model):
    city_id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(150), nullable=False)
    city_postal_code = db.Column(db.String(10), nullable=False)

class Street(db.Model):
    street_id = db.Column(db.Integer, primary_key=True)
    street_name = db.Column(db.String(150), nullable=False)


class Address(db.Model):
    address_id = db.Column(db.Integer, primary_key=True)
    address_street_Number = db.Column(db.String(10), nullable=True)

    address_city_id = db.Column(db.Integer, db.ForeignKey('city.city_id'), nullable=False)
    address_city = db.relationship('City', backref='addresses')
    address_street_id = db.Column(db.Integer, db.ForeignKey('street.street_id'), nullable=True)
    address_street = db.relationship('Street', backref='addresses')
    address_country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=False)
    address_country = db.relationship('Country', backref='addresses')
