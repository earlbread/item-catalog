class Config(object):
    SECRET_KEY = 'test_secret_key'

class ProdConfig(Config):
    pass

class DevConfig(Config):
    DEBUG = True
