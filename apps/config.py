# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import random
import string
import pymongo
import os


class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

    # Set up the App SECRET_KEY
    SECRET_KEY = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = ''.join(random.choice(string.ascii_lowercase)
                             for i in range(32))


class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    DEBUG = True


config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}

MONGO_DB_HOST = os.getenv("MONGO_DB_HOST", 'mongo_db')
MONGO_DB_USER = os.getenv("MONGO_DB_USER", "tpopoviciu")
MONGO_DB_PASS = os.getenv("MONGO_DB_PASS", "tpopoviciu_db_pass")
connection_string = "mongodb://"+ MONGO_DB_USER + ":"+ MONGO_DB_PASS + "@" + MONGO_DB_HOST + ":27017/admin"

client = pymongo.MongoClient("localhost",27017)
db = client.databasePopoviciu
