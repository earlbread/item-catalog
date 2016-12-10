class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test_secret_key'

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://catalog:catalog@localhost:5432/catalog'

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///catalog.db'
