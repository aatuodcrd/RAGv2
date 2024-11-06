import sys
import os
import env.settings as ENV
from pymongo.mongo_client import MongoClient

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

users_collection = MongoClient(ENV.MONGO_URI)[ENV.MONGO_PROJECT_DATABASE][ENV.MONGO_USERS_COLLECTION]
chatlogs_collection = MongoClient(ENV.MONGO_URI)[ENV.MONGO_PROJECT_DATABASE][ENV.MONGO_CHATLOGS_COLLECTION]