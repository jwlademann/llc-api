import os

class Config(object):
    DEBUG = False
    LLC_REGISTER_URL = os.getenv('LLC_REGISTER_URL', 'http://localhost:5002')

class DevelopmentConfig(Config):
    DEBUG = True

class TestConfig(DevelopmentConfig):
    TESTING = True
