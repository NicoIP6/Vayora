import flask_sqlalchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#username:password@localhost:5432
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///Vayora'
db = SQLAlchemy(app)

class Users(db.Model):
    Users_id = db.Column(db.Integer, primary_key=True)
    Users_FirstName = db.Column(db.String(150))
    Users_LastName = db.Column(db.String(150))
    Users_Email = db.Column(db.String(250))
    Users_Phone = db.Column(db.String(20))
    Users_Birthday = db.Column(db.Date)
    Users_BestDistance = db.Column(db.Integer, default=0)
    Users_Validator = db.Column(db.Boolean, default=False)

class Flight(db.Model):
    Flight_id = db.Column(db.Integer, primary_key=True)
    Flight_StartHour = db.Column(db.Time, nullable=False)
    Flight_EndHour = db.Column(db.Time, nullable=False)
    Flight_Distance = db.Column(db.Integer, nullable=True)
    Flight_MaxHeight = db.Column(db.Integer, nullable=False)
    Flight_Landing = db.Column(db.String(250), nullable=True)
    Flight_Users = db.relationship('Users', backref='flight')
    Flight_TakeOff = db.relationship('TakeOff', backref='flight')

class TakeOff(db.Model):
    TakeOff_id = db.Column(db.Integer, primary_key=True)
    TakeOff_Name = db.Column(db.String(150), nullable=False)
    TakeOff_Latitude = db.Column(db.Float, nullable=False)
    TakeOff_Longitude = db.Column(db.Float, nullable=False)
    TakeOff_Type = db.Column(db.String(150), nullable=True)
    TakeOff_DirectionDegreeMin = db.Column(db.Integer, nullable=False)
    TakeOff_DirectionDegreeMax = db.Column(db.Integer, nullable=False)
    TakeOff_GlobalDirection = db.Column(db.String(150), nullable=False)
    TakeOff_Elevation = db.Column(db.Integer, nullable=False)
    TakOff_VerticalDrop = db.Column(db.Integer, nullable=False)
    TakeOff_Difficulty = db.Column(db.String(30), nullable=False)
    TakeOff_Comment = db.Column(db.Text, nullable= True)
