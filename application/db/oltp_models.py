from application.extensions import db, bcrypt, login_manager
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import TIMESTAMP


@login_manager.user_loader
def load_user(user_id):
    return Pilot.query.get(int(user_id))

class Pilot(db.Model, UserMixin):
    __bind_key__ = None

    pilot_id = db.Column(db.Integer, primary_key=True)
    pilot_number = db.Column(db.Integer, nullable=False)
    pilot_firstname = db.Column(db.String(150), nullable=False)
    pilot_lastname = db.Column(db.String(150), nullable=False)
    pilot_email = db.Column(db.String(250), nullable=False)
    pilot_phone = db.Column(db.String(20))
    pilot_birthday = db.Column(db.Date)
    pilot_address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))
    pilot_address = db.relationship('Address', backref='users')
    pilot_maxdistance = db.Column(db.Integer, nullable=True)
    pilot_license_number = db.Column(db.String(150), nullable=True)
    pilot_validator = db.Column(db.Boolean, default=False)
    pilot_validator_score = db.Column(db.Integer, nullable=True)
    pilot_password_hash = db.Column(db.String(128), nullable=False)

    def get_id(self):
        return str(self.pilot_id)

    def set_password(self, password):
        self.pilot_password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.pilot_password_hash, password)

class Takeoff(db.Model):
    __bind_key__ = None

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
    __bind_key__ = None

    flight_id = db.Column(db.Integer, primary_key=True)
    flight_starttime = db.Column(TIMESTAMP(timezone=False, precision=0), nullable=False)
    flight_airtime = db.Column(db.Time, nullable=False)
    flight_distance = db.Column(db.Integer, nullable=True)
    flight_maxheight = db.Column(db.Integer, nullable=True)
    flight_pilot_id = db.Column(db.Integer, db.ForeignKey('pilot.pilot_id'), nullable=False)
    flight_pilot = db.relationship('Pilot', backref='flights')
    flight_takeoff_id = db.Column(db.Integer, db.ForeignKey('takeoff.takeoff_id'))
    flight_takeoff = db.relationship('Takeoff', backref='flights')

class Country(db.Model):
    __bind_key__ = None

    country_id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(150), nullable=False)
    country_code = db.Column(db.String(2), nullable=False)

class City(db.Model):
    __bind_key__ = None

    city_id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(150), nullable=False, unique=True)
    city_postal_code = db.Column(db.String(10), nullable=False)

class Street(db.Model):
    __bind_key__ = None

    street_id = db.Column(db.Integer, primary_key=True)
    street_name = db.Column(db.String(150), nullable=False, unique=True)


class Address(db.Model):
    __bind_key__ = None

    address_id = db.Column(db.Integer, primary_key=True)
    address_street_number = db.Column(db.String(10), nullable=True)

    address_city_id = db.Column(db.Integer, db.ForeignKey('city.city_id'), nullable=False)
    address_city = db.relationship('City', backref='addresses')
    address_street_id = db.Column(db.Integer, db.ForeignKey('street.street_id'), nullable=True)
    address_street = db.relationship('Street', backref='addresses')
    address_country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=False)
    address_country = db.relationship('Country', backref='addresses')

    __table_args__ = (
        db.UniqueConstraint(address_street_number, address_city_id, address_street_id, address_country_id),
    )


