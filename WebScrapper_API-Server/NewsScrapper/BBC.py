import requests
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict
import json

class Url():
    def __init__(self, url:str, query:(Dict|None)) -> None:
        if query != None:        
            self.baseUrl = url
            self.Url = self.baseUrl + '?'
            for key, value in query.items():
                self.Url = self.Url + f'{key}={value}&'
            self.Url = self.Url[0:-1]
            return
        else:
            self.Url = url
            return
        
    def __str__(self) -> str:
        return self.Url
    
    def __repr__(self) -> str:
        return self.Url

class Article():
    id: (str | None)
    type: str
    source: str
    url: str
    title: str
    authors: (List[str] | None)
    topics: List[str]
    body: (str | None)
    publishedAt: str
    summarizedStatus: (str | None)

    def __init__(self,data):
        self.id = None
        self.type = data.get('type')
        self.source = data.get('source')
        self.url = data.get('url')
        self.title = data.get('title')
        self.authors = None
        self.topics = data.get('topics')
        self.body = None
        self.publishedAt = data.get('publishedAt')
        self.summarizedStatus = False

        self.scrape()
        return
    
    def scrape(self) -> None:
        try:
            WEBPAGE = requests.get(url=self.url)
            if WEBPAGE.status_code != 200:
                raise Exception('REQUESTS ERROR: error during request.get(url)')
            soup = BeautifulSoup(WEBPAGE.text, 'html5lib')
            ARTICLEBODY = [f'{element.text}\n' for element in soup.find_all('div',{'data-component':'text-block'})]
            self.body = ''.join(ARTICLEBODY)
            self.body = str(self.body)
            return

        except Exception as e:
            return e
        
    def getData(self) -> Dict:
        DATA = dict({"id":None, "type":self.type, "source":self.source, "url":self.url, "title":self.title, "authors":self.authors, "topics":self.topics, "body":self.body, "publishedAt":self.publishedAt, "summarizedStatus":self.summarizedStatus})
        return DATA
        
    def __str__(self):
        value = f'Article Data\n{self.type}\n{self.topics}\n{self.source}\n{self.url}\n{self.authors}\n{self.publishedAt}\n{self.title}\n{self.body}'
        return value

class BBC():

    SOURCE:str = "BBC"
    BASEURL:str = "https://www.bbc.com"
    API_QUERY:Dict = {'country':'np','page':0}
    BBC_Technology_News_API:str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/092c7c94-aa9b-4933-9349-eb942b3bde77"
    BBC_ScienceHealth_News_API:str = ""
    BBC_AI_NEWS_API:str = ""

    def __init__(self) -> None:
        return
    
    def getArticle(self):
        self.API_QUERY.update({'size':1})
        API = Url(url=self.BBC_Technology_News_API, query=self.API_QUERY)
        
        try:
            request = requests.get(url=API)
            if request.status_code != 200:
                raise Exception('REQUESTS ERROR: error during request.get(url)')
            
            # get only single data from list of data [as only data is requested only one data is there in data so pop it]
            request = list(dict(json.loads(request.content)).get('data')).pop()
            
            DATA = dict(
                {
                    'id':None,
                    "type":list([request.get('type'),request.get('subtype')]),
                    "source":self.SOURCE,
                    "url":self.BASEURL + request.get('path'),
                    "title":request.get('title'),
                    "topics":list(request.get('topics')),
                    "publishedAt":request.get('lastPublishedAt')
                }
            )

            ARTICLE = Article(data=DATA)
            return ARTICLE.getData()

        except Exception as e:
            print('An error occured during fetching News Data',e)
            return str(e)       

    def getArticles(self, size):
        self.API_QUERY.update({'size':size})
        API = Url(url=self.BBC_Technology_News_API,query=self.API_QUERY)

        try:
            request = requests.get(url=API)
            if request.status_code != 200:
                raise Exception('REQUESTS ERROR: error during request.get(url)')
            
            request = dict(json.loads(request.content)).get('data')

            # ARTICLES : (List[Article] | List[None]) = list([])
            ARTICLES = []
            for news in request:
                DATA = dict(
                    {
                        'id':None,
                        "type":list([news.get('type'),news.get('subtype')]),
                        "source":self.SOURCE,
                        "url":self.BASEURL + news.get('path'),
                        "title":news.get('title'),
                        "topics":list(news.get('topics')),
                        "publishedAt":news.get('lastPublishedAt')
                    }
                )
                ARTICLE = Article(data=DATA)
                ARTICLES.append(ARTICLE.getData())

            return ARTICLES
        except Exception as e:
            return e