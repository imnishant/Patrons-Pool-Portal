import os.path

from flask import Flask
from flask_login import LoginManager
from pymongo import MongoClient

from config import app_config

from flask_dance.contrib.google import make_google_blueprint, google


my_path = os.path.abspath(os.path.dirname(__file__))

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'hello'
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile(os.path.join(my_path, '../config.py'))
    app.config.from_pyfile(os.path.join(my_path, '../config.py'))
    return app


# configuring the Flask app and SQLAlchemy
app = create_app(config_name="config")
client = MongoClient()
db = client['FYP']





#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
GOOGLE_CLIENT_ID=os.environ.get('CLIENT_ID')
GOOGLE_CLIENT_SECRET=os.environ.get('CLIENT_SECRET')
google_blueprint = make_google_blueprint(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_CLIENT_SECRET)
app.register_blueprint(google_blueprint, url_prefix='/login')
login_manager = LoginManager(app)
login_manager.init_app(app)



# running the Flask App in debugging mode
#if __name__ == "__main__":
   # app.run(debug=True)

from app import models, routes

