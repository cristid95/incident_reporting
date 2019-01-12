"""This module is to configure app to connect with database."""

from pymongo import MongoClient
from bson.objectid import ObjectId

DATABASE = MongoClient()['incidents'] # DB_NAME
DEBUG = True
client = MongoClient('localhost', 27017)
