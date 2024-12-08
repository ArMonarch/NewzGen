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
    summarized_status: bool

    def __init__(self,data):
        self.id = None
        self.type = data.get('type')
        self.source = data.get('source')
        self.url = data.get('url')
        self.title = data.get('title')
        self.authors = None
        self.topics = data.get('topics')
        self.body = None
        self.publisheddate = data.get('publishedAt')
        self.summarized_status = False

        self.scrape()
        return
    
    def scrape(self) -> None:
        try:
            WEBPAGE = requests.get(url=self.url)
            if WEBPAGE.status_code != 200:
                raise Exception('REQUESTS ERROR: error during request.get(url)')
            soup = BeautifulSoup(WEBPAGE.text, 'html5lib')
            ARTICLEBODY = [f'{element.text}\n' for element in soup.find_all('div',{'data-component':'text-block'})]
            if ARTICLEBODY.__len__() == 0:
                return
            
            self.body = ''.join(ARTICLEBODY)
            self.body = str(self.body)
            return

        except Exception as e:
            return e
        
    def getData(self) -> Dict:
        DATA = dict({"id":None, "type":self.type, "source":self.source, "url":self.url, "title":self.title, "authors":self.authors, "topics":self.topics, "body":self.body, "publisheddate":self.publisheddate, "summarized_status":self.summarized_status})
        return DATA
        
    def __str__(self):
        value = f'Article Data\n{self.type}\n{self.topics}\n{self.source}\n{self.url}\n{self.authors}\n{self.publishedAt}\n{self.title}\n{self.body}'
        return value

class BBC():

    SOURCE : str = "BBC"
    BASEURL : str = "https://www.bbc.com"
    API : str = ""
    API_QUERY : Dict = {'country':'uk','page':0}
    BBC_US_ELECTION_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/37cc4793-d90a-4e83-993d-36c4144c8d5f"
    BBC_US_CANADA_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/db5543a3-7985-4b9e-8fe0-2ac6470ea45b"
    BBC_UK_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/27d91e93-c35c-4e30-87bf-1bd443496470"
    BBC_AFRICA_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/f7905f4a-3031-4e07-ac0c-ad31eeb6a08e"
    BBC_ASIA_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/ec977d36-fc91-419e-a860-b151836c176b"
    BBC_AUSTRALIA_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/3307dc97-b7f0-47be-a1fb-c988b447cc72"
    BBC_EUROPE_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/e2cc1064-8367-4b1e-9fb7-aed170edc48f"
    BBC_LATIN_AMERICA_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/16d132f4-d562-4256-8b68-743fe23dab8c"
    BBC_MIDDLE_EAST_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/b08a1d2f-6911-4738-825a-767895b8bfc4"
    BBC_ScienceHealth_News_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/ebcca993-0219-4ae3-b574-ef54af9d860d"
    BBC_AI_NEWS_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/6d032332-6ce5-425b-85a6-f260355718b3"
    BBC_Technology_News_API : str = "https://web-cdn.api.bbci.co.uk/xd/content-collection/092c7c94-aa9b-4933-9349-eb942b3bde77"

    def __init__(self) -> None:
        return
        
    def getTopicAPI(self, topic) -> str:
        match topic.lower():
            case "us-election":
                self.API = self.BBC_US_ELECTION_API
            
            case "us-canada":
                self.API = self.BBC_US_CANADA_API

            case "uk":
                self.API = self.BBC_UK_API

            case "africa":
                self.API = self.BBC_AFRICA_API

            case "asia":
                self.API = self.BBC_ASIA_API
            
            case "australia":
                self.API = self.BBC_AUSTRALIA_API
            
            case "europe":
                self.API = self.BBC_EUROPE_API

            case "latin-america":
                self.API = self.BBC_LATIN_AMERICA_API
            
            case "middle-east":
                self.API = self.BBC_MIDDLE_EAST_API
            
            case "science-health":
                self.API = self.BBC_ScienceHealth_News_API
            
            case 'ai-news':
                self.API = self.BBC_AI_NEWS_API
            
            case "technology":
                self.API = self.BBC_Technology_News_API

            case _:
                raise Exception("QUERY ERROR: Invalid Topic Submitted")
            
        return self.API
    
    def getArticle(self,topic, page=0):

        self.getTopicAPI(topic=topic)

        self.API_QUERY.update({'page':page,'size':1})
        API = Url(url=self.API, query=self.API_QUERY)
        
        try:
            request = requests.get(url=API)
            if request.status_code != 200:
                raise Exception('REQUESTS ERROR: error during request.get(url)')
            
            # get only single data from list of data [as only data is requested only one data is there in data so pop it]
            if list(dict(json.loads(request.content)).get('data')).__len__() == 0:
                return None
            
            request = list(dict(json.loads(request.content)).get('data')).pop()
            
            DATA = dict(
                {
                    'id':None,
                    "type":list([request.get('type'),request.get('subtype')]),
                    "source":self.SOURCE,
                    "url":self.BASEURL + request.get('path'),
                    "title":request.get('title'),
                    "topics":list(request.get('topics')) if list(request.get('topics')).__len__() != 0 else list([topic]),
                    "publishedAt":request.get('lastPublishedAt')
                }
            )

            ARTICLE = Article(data=DATA)
            return ARTICLE.getData()

        except Exception as e:
            print('An error occured during fetching News Data',e)
            return str(e)

    def getArticles(self, size = 1):
        
        if size == None:
            size = 1

        self.API_QUERY.update({'size':size})
        
        API = Url(url=self.API,query=self.API_QUERY)

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
            return str(e)