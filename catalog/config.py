import os

class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test_secret_key'

    GOOGLE_CLIENT_ID     = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    FB_CLIENT_ID         = os.environ.get('FB_CLIENT_ID')
    FB_CLIENT_SECRET     = os.environ.get('FB_CLIENT_SECRET')

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://catalog:catalog@localhost:5432/catalog'

class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///catalog.db'
