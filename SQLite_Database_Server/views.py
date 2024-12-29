from flask import Blueprint, request
from typing import Dict
import json
import sqlite3
from SQLCommands import INSERT_ARTICLE_WITH_ID, INSERT_ARTICLE_WITHOUT_ID, GET_ARTICLE_WITH_ID, GET_ARTICLE_WITH_TITLE, INSERT_SUMMARY_WITH_ID, INSERT_SUMMARY_WITHOUT_ID, GET_SUMMARY_WITH_ID, GET_SUMMARY_WITH_ARTICLEID, GET_ONE_UNSUMMARIZED_ARTICLE, UPDATE_ARTICLE_STATUS_UNSUMMARIZED, UPDATE_ARTICLE_STATUS_PENDING, UPDATE_ARTICLE_STATUS_SUMMARIZED
from config import DATABASE_PATH

# create blueprint for the views
api = Blueprint('api', __name__)

# functional route to insert Article to database
@api.route('/add/article', methods=['POST'])
def Article_Insert() -> str:

    try:
        if request.method != 'POST':
            raise Exception('METHOD ERROR: route only supports POST method')
        
        DATA : dict = dict(json.loads(request.data))
    
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()

        if DATA.get('title'):
            TYPE : str = ','.join(DATA.get('type'))
            TOPICS : str = ','.join(DATA.get('topics'))

            DATA.update({'type': TYPE, 'topics': TOPICS})
            
            if DATA.get('id'):
                cursor.execute(INSERT_ARTICLE_WITH_ID, DATA)
            
            elif not DATA.get('id'):
                cursor.execute(INSERT_ARTICLE_WITHOUT_ID, DATA)

            cursor.close()
            connection.commit()
            connection.close()
            
            return ('Pass',201)
        
        else:
            raise Exception('VALUE ERROR: Required fields missing in (id (optional), type, authors, topics, body, publisheddate, source, url, summarized_status)')
    
    except sqlite3.Error as e:
        return (f'SQL Error:{e.sqlite_errorname}, ErrorCode: {e.sqlite_errorcode}', 403)
    
    except Exception as e:
        print(e)
        return (str(e),401)
         
# functional route to get a single id with Id & Title = -----------
@api.route('/get/article',methods=['POST'])
def getArticle():

    try:
        if request.method != "POST":
            raise Exception("METHOD ERROR: route only supports POST method")
        
        DATA : Dict = dict(json.loads(request.data))

        # Connect to database to get article data
        databaseConnection = sqlite3.connect(DATABASE_PATH)
        cursor = databaseConnection.cursor()

        if DATA.get('article_id') != None:
            Article = cursor.execute(GET_ARTICLE_WITH_ID,{'article_id': int(DATA.get('article_id'))})
            ID, TYPE, AUTHORS, TITLE, TOPICS, BODY, PUBLISHEDDATE, SOURCE, URL, SUMMARIZEDSTATUS = Article.fetchone()
            

        elif DATA.get('title') != None:
            Article = cursor.execute(GET_ARTICLE_WITH_TITLE,{'title': str(DATA.get('title'))})
            ID, TYPE, AUTHORS, TITLE, TOPICS, BODY, PUBLISHEDDATE, SOURCE, URL, SUMMARIZEDSTATUS = Article.fetchone()
            
        else:
            raise Exception("QUERY ERROR: Must provide Query article_id OR title")
        
        cursor.close()
        databaseConnection.close()
        
        TYPE = TYPE.split(',')
        TOPICS = TOPICS.split(',')
        
        ARTICLE = dict({'id':ID,'type':TYPE,'authors':AUTHORS,'title':TITLE,'topics':TOPICS,'body':BODY,'publisheddate':PUBLISHEDDATE,'source':SOURCE,'url':URL,'summarized_status':SUMMARIZEDSTATUS})
        return (ARTICLE, 201)
    
    except sqlite3.Error as e:
        return (f'SQL Error:{e.sqlite_errorname}, ErrorCode: {e.sqlite_errorcode}', 403)
    
    except TypeError as e:
        return ('DATA ERROR: Data Not Found OR Data doesn\'t EXISTS', 404)
    
    except Exception as e:
        return (str(e), 401)
    
@api.route('/add/article-summary', methods=['POST'])
def ArticleSummary_Insert():
    
    try:
        if request.method != 'POST':
            raise Exception('METHOD ERROR: route only supports POST method')
        
        DATA : dict = dict(json.loads(request.data))

        # Connect to the database
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        
        if DATA.get('article_id') != None and DATA.get('llm_used') != None and DATA.get('generated_summary') != None:
            
            last_rowid: int = -1
            if DATA.get('id'):
                cursor.execute(INSERT_SUMMARY_WITH_ID, DATA)
                last_rowid = cursor.lastrowid if cursor.lastrowid != None else -1

            elif not DATA.get('id'):
                cursor.execute(INSERT_SUMMARY_WITHOUT_ID, DATA)
                last_rowid = cursor.lastrowid if cursor.lastrowid != None else -1

            cursor.close()
            connection.commit()
            connection.close()

            return (str(last_rowid),201)

        else:
            raise Exception('VALUE ERROR: Required fields missing in (id (optional) ,article_id, llm_used, generated_summary)')
        
    except sqlite3.Error as e:
        return (f'SQL Error:{e.sqlite_errorname}, ErrorCode: {e.sqlite_errorcode}', 403)

    except Exception as e:
        return (str(e), 401)   

@api.route('/get/article-summary',methods=['POST'])
def getArticleSummary():

    try:
        if request.method != 'POST':
            raise Exception("METHOD ERROR: route only supports POST method")
        
        DATA : dict = dict(json.loads(request.data))

        # Connect to database to get article data
        databaseConnection = sqlite3.connect(DATABASE_PATH)
        cursor = databaseConnection.cursor()

        if DATA.get('summary_id'):
            summary = cursor.execute(GET_SUMMARY_WITH_ID, DATA)
            ID, ARTICLE_ID, LLM_USED, GENERATED_SUMMARY = summary.fetchone()

        elif DATA.get('article_id'):
            summary = cursor.execute(GET_SUMMARY_WITH_ARTICLEID, DATA)
            ID, ARTICLE_ID, LLM_USED, GENERATED_SUMMARY = summary.fetchone()
        
        else:
            raise Exception('QUERY ERROR: Required fields missing in (summary_id, article_id) *one required')
        
        SUMMARY : dict = dict({
            'id': ID,
            'article_id': ARTICLE_ID,
            'llm_used': LLM_USED,
            'generated_summary': GENERATED_SUMMARY
        })

        cursor.close()
        databaseConnection.close()

        return (SUMMARY, 201)
    
    except sqlite3.Error as e:
        return (f'SQL Error:{e.sqlite_errorname}, ErrorCode: {e.sqlite_errorcode}', 403)
    
    except TypeError as e:
        return ('', 404)
    
    except Exception as e:
        return (str(e), 401)
    
@api.route("/get/unsummarized/article", methods=["GET"])
def getOneUnsummarizedArticle():
    try:
        if request.method != "GET":
            raise Exception("METHOD ERROR: route only supports GET method")
        
        # Connect to the database
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()

        Article = cursor.execute(GET_ONE_UNSUMMARIZED_ARTICLE)
        ID, TYPE, AUTHORS, TITLE, TOPICS, BODY, PUBLISHEDDATE, SOURCE, URL, SUMMARIZEDSTATUS = Article.fetchone()

        cursor.close()
        connection.close()

        TYPE = TYPE.split(',')
        TOPICS = TOPICS.split(',')
        
        ARTICLE = dict({'id':ID,'type':TYPE,'authors':AUTHORS,'title':TITLE,'topics':TOPICS,'body':BODY,'publisheddate':PUBLISHEDDATE,'source':SOURCE,'url':URL,'summarized_status':SUMMARIZEDSTATUS})                
        return (ARTICLE, 201)

    except TypeError as e:
        return ("DATA ERROR: Data Not Found OR Data doesn\'t EXISTS",404)
    
    except Exception as e:
        print(str(e))
        return (str(e), 401)

# Function to update the Article from Articles table Summarized_Status to unsummarized
@api.route("/update/article/status/unsummarized", methods=["POST"])
def Update_Status_Unsummarized():
    try:
        Article_Id = dict(json.loads(request.data)).get("id")

        if request.method != "POST":
            raise Exception("METHOD ERROR: route only supports GET method")
    
        if not Article_Id:
            raise Exception("QUERY ERROR: Required id field missing")
        
        if type(Article_Id) != int:
            raise Exception("QUERY ERROR: Required id field must be int")
        
        # Connect to the database
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        
        cursor.execute(UPDATE_ARTICLE_STATUS_UNSUMMARIZED, dict({"id":Article_Id}))
        
        cursor.close()
        connection.commit()
        connection.close()

        return("",201)
    
    except Exception as e:
        return (str(e), 401)

# Function to update the Article from Articles table Summarized_Status to Pending
@api.route("/update/article/status/pending", methods=["POST"])
def Update_Status_Pending():
    try:
        Article_Id = dict(json.loads(request.data)).get("id")
        
        if request.method != "POST":
            raise Exception("METHOD ERROR: route only supports GET method")
    
        if not Article_Id:
            raise Exception("QUERY ERROR: Required id field missing")
        
        if type(Article_Id) != int:
            raise Exception("QUERY ERROR: Required id field must be int")
        
        
        # connect to database
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()

        cursor.execute(UPDATE_ARTICLE_STATUS_PENDING, dict({"id":Article_Id}))
        
        cursor.close()
        connection.commit()
        connection.close()

        return("",201)
    
    except Exception as e:
        return (str(e), 401)

# Function to update the Article from Articles table Summarized_Status to summarized
@api.route("/update/article/status/summarized", methods=["POST"])
def Update_Status_Summarized():
    try:
        Article_Id = dict(json.loads(request.data)).get("id")

        if request.method != "POST":
            raise Exception("METHOD ERROR: route only supports GET method")
    
        if not Article_Id:
            raise Exception("QUERY ERROR: Required id field missing")
        
        if type(Article_Id) != int:
            raise Exception("QUERY ERROR: Required id field must be int")
        
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        
        cursor.execute(UPDATE_ARTICLE_STATUS_SUMMARIZED, dict({"id":Article_Id}))

        # commit and close the database connection
        cursor.close()
        connection.commit()
        connection.close()

        return("",201)
    
    except Exception as e:
        return (str(e), 401)

    
# Route to check if the database is empty
    
@api.route('/database/empty',methods=['GET'])
def check_IsEmpty():
    try:
        if request.method != 'GET':
            raise Exception("METHOD ERROR: route only supports GET method")
        
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM Articles")
        ROWS = cursor.fetchone()

        cursor.close()
        connection.close()

        if int(ROWS[0]) != 0:
            return ("False",201)
        else:
            return ("True",201)
    
    except Exception as e:
        return(str(e),401)
