from flask import Blueprint, request
import json
import sqlite3
from sqlite3 import OperationalError
# from extension import sqlite3
from SQLCommands import INSERT_ARTICLE_WITHOUT_ID, INSERT_ARTICLE_WITH_ID

# create blueprint for the views
api = Blueprint('api', __name__)

@api.route('hello', methods=['GET'])
def hello():
    return "Hello World!"


# functional route to insert Article to database
@api.route('/add/article', methods=['POST'])
def Article_Insert():
    if request.method == 'POST':
        try:
            ArticleData = dict(json.loads(request.data))
            if ArticleData['type'] != "" and ArticleData['authors'] == "" and ArticleData['topics'] == "" and ArticleData['body'] == "" and ArticleData['publisheddate'] == ""  and ArticleData['source'] == "" and ArticleData['summarized_status'] == "":            
                print("Some of the Data Fields are missing!!")
                return "400"

            DatabaseConnection = sqlite3.connect("/home/frenzfries/dev/NewzGen_News-Scrapper-Summarization/SQLite_Database_Server/data/NewzData.db")
            cursor = DatabaseConnection.cursor()

            try:
                cursor.execute(INSERT_ARTICLE_WITHOUT_ID, ArticleData)
            
            except OperationalError:
                print("There is an error in SQL Query")

            cursor.close()
            DatabaseConnection.commit()
            DatabaseConnection.close()
            
            return "200"
        
        except KeyError:
            print("Important Data Field Missing!!")
            return "400"

        except ValueError:
            print("Decoding JSON has failed")
            return "400"
            