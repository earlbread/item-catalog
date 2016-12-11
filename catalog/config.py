class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test_secret_key'

    GOOGLE_CLIENT_ID='YOUR_GOOGLE_CLIENT_ID'
    GOOGLE_CLIENT_SECRET='YOUR_GOOGLE_CLIENT_SECRET'
    FB_CLIENT_ID='YOUR_FACEBOOK_CLIENT_ID'
    FB_CLIENT_SECRET='YOUR_FACEBOOK_CLIENT_SECRET'

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://catalog:catalog@localhost:5432/catalog'

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///catalog.db'
