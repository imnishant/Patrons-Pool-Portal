import os.path

from flask import Flask
from pymongo import MongoClient
from flask_mail import Mail

from config import app_config

my_path = os.path.abspath(os.path.dirname(__file__))
BLOB = os.path.join(my_path, 'static/BLOB')


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'hello'
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile(os.path.join(my_path, '../config.py'))
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 2525

    return app


# configuring the Flask app and SQLAlchemy
app: Flask = create_app(config_name="config")
client = MongoClient()
db = client['FYP']
mail = Mail(app)

# The below command in the database to enable the search functionality
db['user'].create_index([('email', 'text'), ('isSponsor', 'text'), ('posts.post_type', 'text'), ('posts.post_headline', 'text'), ('posts.base_price', 'text')])

# running the Flask App in debugging mode
#if __name__ == "__main__":
   # app.run(debug=True)

from app import models, routes

