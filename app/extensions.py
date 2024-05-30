# app/extensions.py

from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
from flask import Flask
from app.config import Config
from flask_mail import Mail

bcrypt = Bcrypt()
jwt = JWTManager()
client = MongoClient(Config.MONGO_URI)
db = client['cluster0']
mail = Mail()

def init_app(app: Flask):
    app.config.from_object(Config)
    bcrypt.init_app(app)
    jwt.init_app(app)
