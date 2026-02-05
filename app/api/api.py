from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import json



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///Vayora.db' #username:password@localhost:5432
db = SQLAlchemy(app)