from flask import Blueprint, request
from typing import Dict
import json
import sqlite3
from SQLCommands import INSERT_ARTICLE_WITH_ID, INSERT_ARTICLE_WITHOUT_ID, GET_ARTICLE_WITH_ID, GET_ARTICLE_WITH_TITLE, INSERT_SUMMARY_WITH_ID, INSERT_SUMMARY_WITHOUT_ID, GET_SUMMARY_WITH_ID, GET_SUMMARY_WITH_ARTICLEID
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
            
            return ('Pass',201)
        
        else:
            raise Exception('VALUE ERROR: Required fields missing in (id (optional), type, authors, topics, body, publisheddate, source, url, summarized_status)')
    
    except sqlite3.Error as e:
        return (f'SQL Error:{e.sqlite_errorname}, ErrorCode: {e.sqlite_errorcode}', 403)
    
    except Exception as e:
        print(e)
        return (str(e),401)
    
    finally:
        cursor.close()
        connection.commit()
        connection.close()
        
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
        
        TYPE = TYPE.split(',')
        TOPICS = TOPICS.split(',')
        
        ARTICLE = dict({'id':ID,'type':TYPE,'authors':AUTHORS,'title':TITLE,'topics':TOPICS,'body':BODY,'publisheddate':PUBLISHEDDATE,'source':SOURCE,'url':URL,'summarized_status':bool(True) if SUMMARIZEDSTATUS=='1' else bool(False)})                
        return (ARTICLE, 201)
    
    except sqlite3.Error as e:
        return (f'SQL Error:{e.sqlite_errorname}, ErrorCode: {e.sqlite_errorcode}', 403)
    
    except TypeError as e:
        return ('DATA ERROR: Data Not Found OR Data doesn\'t EXISTS', 404)
    
    except Exception as e:
        return (str(e), 401)
    
    finally:
        cursor.close()
        databaseConnection.close()
    
    
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
            
            if DATA.get('id'):
                cursor.execute(INSERT_SUMMARY_WITH_ID, DATA)

            elif not DATA.get('id'):
                cursor.execute(INSERT_SUMMARY_WITHOUT_ID, DATA)

            return ('',201)

        else:
            raise Exception('VALUE ERROR: Required fields missing in (id (optional) ,article_id, llm_used, generated_summary)')
        
    except sqlite3.Error as e:
        return (f'SQL Error:{e.sqlite_errorname}, ErrorCode: {e.sqlite_errorcode}', 403)

    except Exception as e:
        return (str(e), 401)
    
    finally:
        cursor.close()
        connection.commit()
        connection.close()

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

        return (SUMMARY, 201)
    
    except sqlite3.Error as e:
        return (f'SQL Error:{e.sqlite_errorname}, ErrorCode: {e.sqlite_errorcode}', 403)
    
    except TypeError as e:
        return ('DATA ERROR: Data Not Found OR Data doesn\'t EXISTS', 404)
    
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

        if int(ROWS[0]) != 0:
            return ("False",201)
        else:
            return ("True",201)
    
    except Exception as e:
        return(str(e),401)
    
    finally:
        cursor.close()
        connection.close()