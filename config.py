import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Configuration
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    pass

app_config = {
    'config': Config
}