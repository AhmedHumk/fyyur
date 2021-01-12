import os

class InitiateConfig:
    SECRET_KEY = os.urandom(32)
    basedir = os.path.abspath(os.path.dirname(__file__))
    DEBUG = True
    #DatabaseURI
    DATABASE_NAME = "Your Database Name"
    username = "Your database user"
    password = "Your database password"
    url = "localhost:5432"
    SQLALCHEMY_DATABASE_URI = "postgres://{}:{}@{}/{}".format(
        username, password, url, DATABASE_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
