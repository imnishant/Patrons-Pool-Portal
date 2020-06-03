import os.path

from flask import Flask
from flask_pymongo import PyMongo
from flask_mail import Mail

from config import app_config

my_path = os.path.abspath(os.path.dirname(__file__))
BLOB = os.path.join(my_path, 'static/BLOB')


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    # Uncomment the below line when building up the docker image
    # app.config['MONGO_URI'] = "mongodb://mongo:27017/FYP"
    # Comment the below line when you building the docker image and uncomment the above line
    app.config['MONGO_URI'] = "mongodb://localhost:27017/FYP"
    app.secret_key = 'hello'
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile(os.path.join(my_path, '../config.py'))
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config["MAIL_USE_SSL"] = True
    app.config['MAIL_USERNAME'] = 'patronspoolupdates@gmail.com'
    app.config['MAIL_DEFAULT_SENDER'] = 'patronspoolupdates@gmail.com'
    app.config['MAIL_PASSWORD'] = 'hcmrrkqbdqyoyolf'
    return app


# configuring the Flask app and PyMongo
app: Flask = create_app(config_name="config")
mongo = PyMongo(app)
db = mongo.db
mail = Mail(app)

# The below command in the database to enable the search functionality
db['user'].create_index([('email', 'text'), ('isSponsor', 'text'), ('posts.post_type', 'text'), ('posts.post_headline', 'text'), ('posts.base_price', 'text')])

from app import models, routes

