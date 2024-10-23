from flask import Blueprint, request
from typing import List
from NewsScrapper.BBC import BBC, Article

# create blueprint for the views
api = Blueprint('api',__name__)


# routes
@api.route('/get/article',methods=['GET'])
def getArticle():
    bbc = BBC()
    article:Article = bbc.getArticle()
    return str(article)

@api.route('/get/articles',methods=['GET'])
def getArticles():
    if request.method != 'GET':
        raise Exception("Route only support 'GET' method!")
    
    if request.args.get('size') != None:
        size = request.args.get('size')
    
    elif request.args.get('noOfArticles') != None:
        size = request.args.get('noOfArticles')
    
    if request.args.get('size') != None and request.args.get('noOfArticles') != None:
        size = request.args.get('size')

    bbc = BBC()
    articles:List[Article] = bbc.getArticles(size)
    
    response:str = ''
    for article in articles:
        response = response + str(article) + '\n'

    return response