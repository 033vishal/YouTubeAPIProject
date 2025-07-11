#MongoDB ke saath Python code se connect karne ke liye hota hai
import pymongo
from os import environ, path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# getting SECRETE Mongo_URI
mongoURI = environ.get('MONGO_URI')


# connecting to database
def configDB():
    print('connecting to database...')
    client = pymongo.MongoClient(mongoURI, serverSelectionTimeoutMS=30000)
    database = client.get_database('YoutubeData') # get key "YoutubeData" from mongoDb database , you can change it into another db also
    db = database.ysearch # collection of youtubedata db similarly we can have other collection in same db
    print('Connected to Database!!')
    return db  