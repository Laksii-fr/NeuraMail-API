from pymongo import mongo_client
from app.config import settings

client = mongo_client.MongoClient(settings.DATABASE_URL)
print('MongoDB Connected Successfully...')

db = client[settings.MONGO_INITDB_DATABASE]
UsersCollection = db.users_collection
profiles = db.profiles
SavedQueries = db.SavedQueries