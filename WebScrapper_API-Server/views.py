from flask import Blueprint, request
from NewsScrapper.BBC import BBC

# create blueprint for the views
api = Blueprint(name='WebScrapper',import_name='api')

@api.route('/get/article', methods=['GET'])
def getArticle():
    if request.method != 'GET':
        # raise Exception("METHOD ERROR: route only supports GET method")
        return 'METHOD ERROR: route only supports GET method'
    
    if request.args.get('topic') == None:
        # raise Exception('QUERY ERROR: For this api Query args should be topic')
        return 'QUERY ERROR: For this api Query args should be topic'
    
    Article = BBC().getArticle()
    return Article

@api.route('get/articles',methods=['GET'])
def getArticles():
    return '200'