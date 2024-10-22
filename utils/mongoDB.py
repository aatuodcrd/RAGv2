import sys
import os

# Add the directory containing the 'env' module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import env.settings as ENV
from pymongo.mongo_client import MongoClient

users_collection = MongoClient(ENV.MONGO_URI)[ENV.MONGO_PROJECT_DATABASE][ENV.MONGO_USERS_COLLECTION]
chatlogs_collection = MongoClient(ENV.MONGO_URI)[ENV.MONGO_PROJECT_DATABASE][ENV.MONGO_CHATLOGS_COLLECTION]