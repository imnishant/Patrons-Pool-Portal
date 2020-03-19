from flask import Flask

from config import app_config
from pymongo import MongoClient

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient

import os.path

my_path = os.path.abspath(os.path.dirname(__file__))

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'hello'
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile(os.path.join(my_path, '../config.py'))
    return app


# configuring the Flask app and SQLAlchemy
app = create_app(config_name="config")
client = MongoClient()
db = client['FYP']

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)
# OAuth 2 client setup
client = WebApplicationClient(os.environ.get('GOOGLE_CLIENT_ID'))


# running the Flask App in debugging mode
#if __name__ == "__main__":
   # app.run(debug=True)

from app import models, routes

