from flask import Flask


#dotenv is a library
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# importing controler functions
from task import query, search, start
import asyncio


app = Flask(__name__)

# route for home page
# decorator hai
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# route for quering database  (value)
@app.route("/query")
@app.route("/query/<page>")
def getMongoDBpaginatedData(page=1):
    return query(page)

# route for searching title and discription of videos
@app.route("/search")
@app.route("/search/<tag>")
def getMongoDBSearchQuery(tag=''):
    print(tag)
    data = search(tag)  # call from task.py
    return data

# route for start fetching latest videos from Youtube
@app.route("/start")

def insertLatestVideoTOMongoDB():
    asyncio.run(start())
    return "S"



