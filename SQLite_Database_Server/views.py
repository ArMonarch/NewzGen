from flask import Blueprint, request
from typing import Dict
import json
import sqlite3
from sqlite3 import OperationalError
# from extension import sqlite3
from SQLCommands import INSERT_ARTICLE_WITHOUT_ID, GET_ARTICLE_WITH_ID, GET_SUMMARY_WITH_ID, GET_ARTICLE_WITH_TITLE
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

            DatabaseConnection = sqlite3.connect(DATABASE_PATH)
            cursor = DatabaseConnection.cursor()

            try:
                # change all list to text
                ArticleData['type'] = ','.join(ArticleData.get('type'))
                ArticleData['topics'] = ','.join(ArticleData.get('topics'))
                cursor.execute(INSERT_ARTICLE_WITHOUT_ID, ArticleData)
            
            except OperationalError:
                print("There is an error in SQL Query")

            cursor.close()
            DatabaseConnection.commit()
            DatabaseConnection.close()
            
            return ('', 201)
        
        except KeyError as e:
            print("Important Data Field Missing!!")
            return (str(e), 401)

        except ValueError as e:
            print("Decoding JSON has failed")
            return (str(e), 401)
        
# functional route to get a single id with Id & Title = -----------
@api.route('/get/article',methods=['POST'])
def getArticle():
    if request.method != "POST":
        raise Exception("METHOD ERROR: route only supports POST method")

    # Connect to database to get article data
    databaseConnection = sqlite3.connect(DATABASE_PATH)
    cursor = databaseConnection.cursor()

    try:
        DATA : Dict = dict(json.loads(request.data))

        if DATA.get('articleId') != None:
            Article = cursor.execute(GET_ARTICLE_WITH_ID,{'articleId': int(DATA.get('articleId'))})
            ID, TYPE, AUTHORS, TITLE, TOPICS, BODY, PUBLISHEDDATE, SOURCE, URL, SUMMARIZEDSTATUS = Article.fetchone()

        elif DATA.get('title') != None:
            Article = cursor.execute(GET_ARTICLE_WITH_TITLE,{'title': str(DATA.get('title'))})
            ID, TYPE, AUTHORS, TITLE, TOPICS, BODY, PUBLISHEDDATE, SOURCE, URL, SUMMARIZEDSTATUS = Article.fetchone()
            
        else:
            raise Exception("QUERY ERROR: Must provide Query articleId OR title")
        
        # TODO : Change type and topic back into array after getting text from sqlite
        TYPE = TYPE.split(',')
        TOPICS = TOPICS.split(',')
        
        cursor.close()
        databaseConnection.close()        
        
        ARTICLE = dict({'id':ID,'type':TYPE,'authors':AUTHORS,'title':TITLE,'topics':TOPICS,'body':BODY,'publisheddate':PUBLISHEDDATE,'source':SOURCE,'url':URL,'summarized_status':bool(True) if SUMMARIZEDSTATUS=='1' else bool(False)})                
        return (ARTICLE, 201)
    
    except TypeError as e:
        return ('DATA ERROR: Data Not Found OR Data doesn\'t EXISTS', 404)
    
    except Exception as e:
        # print("An Unecpected error occured while getting data from Database")
        return (str(e), 405)
    
# TODO : Update the Article summary route method to POST asd send query as POST-data

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