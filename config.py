import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    pass


app_config = {
    'config': Config
}