from flask import Blueprint, request
from typing import Dict
import json
import sqlite3
from sqlite3 import OperationalError
# from extension import sqlite3
from SQLCommands import INSERT_ARTICLE_WITHOUT_ID, INSERT_ARTICLE_WITH_ID, GET_ARTICLE_WITH_ID, GET_SUMMARY_WITH_ID
from config import DATABASE_PATH

# create blueprint for the views
api = Blueprint('api', __name__)

@api.route('hello', methods=['GET'])
def hello():
    return "Hello World!"


# functional route to insert Article to database
@api.route('/add/article', methods=['POST'])
def Article_Insert() -> str:
    if request.method == 'POST':
        try:
            ArticleData:Dict = dict(json.loads(request.data))
            if ArticleData['type'] == "" and ArticleData['authors'] == "" and ArticleData['topics'] == "" and ArticleData['body'] == "" and ArticleData['publisheddate'] == ""  and ArticleData['source'] == "" and ArticleData['url'] == "" and ArticleData['summarized_status'] == "":            
                print("Some of the Data Fields are missing!!")
                return "400"

            DatabaseConnection = sqlite3.connect("/home/frenzfries/dev/NewzGen_News-Scrapper-Summarization/SQLite_Database_Server/data/NewzData.db")
            cursor = DatabaseConnection.cursor()

            try:
                print(ArticleData)
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
        
# functional route to get a single id with Id = -----------
@api.route('/get/article',methods=['GET'])
def getArticle():
    if request.method != "GET":
        raise Exception("METHOD ERROR: route only supports GET method")

    if request.args.get('articleId') == None:
        raise Exception("QUERY ERROR: For this api Query args should be articleId=''")

    ArticleId = request.args.get('articleId')

    # Connect to database to get article data
    databaseConnection = sqlite3.connect(DATABASE_PATH)
    cursor = databaseConnection.cursor()

    try:
        Article = cursor.execute(GET_ARTICLE_WITH_ID,{'articleId':ArticleId})
        ID, TYPE, AUTHORS, TITLE, TOPICS, BODY, PUBLISHEDDATE, SOURCE, URL, SUMMARIZEDSTATUS = Article.fetchone()
        
        cursor.close()
        databaseConnection.close()
        
        
        ARTICLE = dict({'id':ID,'type':TYPE,'authors':AUTHORS,'title':TITLE,'topics':TOPICS,'body':BODY,'publishedDate':PUBLISHEDDATE,'source':SOURCE,'url':URL,'summarizedStatus':SUMMARIZEDSTATUS})
                
        return ARTICLE
    except:
        print("An Unecpected error occured while getting data from Database")
        return '400'


@api.route('/get/article-summary',methods=['GET'])
def getArticleSummary():
    if request.method != 'GET':
        raise Exception("METHOD ERROR: route only supports GET method")

    if request.args.get('summaryId') == None:
        raise Exception("QUERY ERROR: For this api Query args should be articleId=''")
    
    SummaryArticleId = request.args.get('summaryId')

    # Connect to database to get article data
    databaseConnection = sqlite3.connect(DATABASE_PATH)
    cursor = databaseConnection.cursor()

    try:
        Summary = cursor.execute(GET_SUMMARY_WITH_ID, {'summaryId':SummaryArticleId})
        ID, ARTICLEID, LLMUSED, GENERATEDSUMMARY = Summary.fetchone()

        cursor.close()
        databaseConnection.close()
        
        SummaryData = dict({'id':ID,'articleId':ARTICLEID,'llmUsed':LLMUSED,'generatedSummary':GENERATEDSUMMARY})
        return SummaryData
    
    except:
        print("An Unecpected error occured while getting data from Database")
        return '400'