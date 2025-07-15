import requests
from db import configDB
from flask import jsonify
from bson.objectid import ObjectId  # Import ObjectId

from os import environ
from dotenv import load_dotenv, find_dotenv

import time
import asyncio

load_dotenv(find_dotenv())   #sensitive details store karte hain.

YOUTUBE_API_URL = environ.get('YOUTUBE_API_URL')

GOOGLE_API_KEY = environ.get('GOOGLE_API_KEY')

db = configDB() #y_search data value --(call)


# controler for quering database and getting paginated responce
def query(page):
    page_limit = 10
    page = int(page)
    # Fetch data from MongoDB, sorting by 'publishTime' in descending order
    data_cursor = db.find().skip((page - 1) * page_limit).limit(page_limit).sort('publishTime', -1)

    Data = []
    for data in data_cursor:
        # Create a mutable copy of the document
        new_data = data.copy()
        # Convert ObjectId to string for JSON serialization
        if '_id' in new_data and isinstance(new_data['_id'], ObjectId):
            new_data['_id'] = str(new_data['_id']) # objectID convert it into str bcz ObjectIds directly JSON mein nahi bhej sakte
        Data.append(new_data)
    return jsonify(Data)


# controler for searching videos using keyword in title or discription
def search(tag):
    # Ensure text index is created (though it's better to do this once outside the function)
    db.create_index([('Title', "text"), ('Description', "text")])

    # Search for documents where 'Title' or 'Description' contain the tag
    data_cursor = db.find({"$text": {"$search": tag}})

    Data = []
    for data in data_cursor:   # MongoDB query se mile har document par loop chalta hai
        # Create a mutable copy of the document
        new_data = data.copy()
        # Convert ObjectId to string for JSON serialization
        if '_id' in new_data and isinstance(new_data['_id'], ObjectId):
            new_data['_id'] = str(new_data['_id'])
        Data.append(new_data)
    return jsonify(Data)


# controler for fetching latest videos from YouTube
async def video_data():

    while True:
        params = {
            "part": "snippet",
            "maxResults": 50,
            "type": "video",
            "key": GOOGLE_API_KEY,
            "publishedAfter": "2020-01-01T00:00:00Z",
            "order": "date",
            "q": "cricket"
        }

        response = requests.get(YOUTUBE_API_URL, params=params)
        print(response)
        DATA_LIST = []
        if response.status_code == 200:
            json_response = response.json()

            for i in json_response.get("items", []):
                video_id = i.get("id", {}).get("videoId")
                snippet_data = i.get("snippet", {})
                if snippet_data:
                    Id = video_id
                    Title = str(i['snippet']['title'])
                    Description = i['snippet']['description']
                    Thumbnails_urls = i['snippet']['thumbnails']['default']['url']

                    DATA = {
                        '_id': Id,  # Using videoId as _id, which is already a string
                        'Title': Title,
                        'Description': Description,
                        'Thumbnails_urls': Thumbnails_urls,
                        'publishTime': i['snippet']['publishedAt'],  # Changed to 'publishedAt' for consistency
                    }
                    DATA_LIST.append(DATA)

            for d in DATA_LIST:
                time.sleep(2)
                # Check if the document already exists using the string _id
                if db.find_one({"_id": d["_id"]}):
                    print('duplicate data')
                else:
                    r = db.insert_one(d)
                    print("Youtube data saved to database!!")
                    print(r.inserted_id)
        time.sleep(10)


# start fetching
async def start():
    loop = asyncio.get_event_loop()
    print('loop started')
    # Use loop.create_task to run video_data as a background task
    loop.create_task(video_data())
    loop.run_forever()  # Keep the event loop running


