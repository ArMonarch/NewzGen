from flask import Blueprint, request, make_response
from NewsScrapper.BBC import BBC
from typing import Dict, List

# create blueprint for the views
api = Blueprint(name='WebScrapper',import_name='api')

@api.route('/bbc/get/article', methods=['GET'])
def getArticle():
    try:
        if request.method != 'GET':
            # raise Exception("METHOD ERROR: route only supports GET method")
            raise Exception('METHOD ERROR: route only supports GET method')

        if request.args.get('topic') == None:
            # raise Exception('QUERY ERROR: For this api Query args should be topic')
            raise Exception('QUERY ERROR: For this api Query args should be topic')
    
        Article : Dict = BBC().getArticle()
        return (Article, 201)
    
    except Exception as e:
        return (str(e), 401)

@api.route('/bbc/get/articles',methods=['GET'])
def getArticles():
    try:
        if request.method != 'GET':
            # raise Exception("METHOD ERROR: route only supports GET method")
            raise Exception('METHOD ERROR: route only supports GET method')

        if request.args.get('topic') == None:
            # raise Exception('QUERY ERROR: For this api Query args should be topic')
            raise Exception('QUERY ERROR: For this api Query args should be topic')
        
        Articles: List[Dict] = BBC().getArticles(int(request.args.get('size')))
        return (Articles, 201)

    except Exception as e:
        return (str(e), 401)