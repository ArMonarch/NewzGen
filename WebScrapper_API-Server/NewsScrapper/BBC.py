import requests
from typing import List, Dict
from bs4 import BeautifulSoup

class Url():
    
    def __init__(self, url:str, query:Dict):
        self.baseUrl = url
        self.query = query

        self.url = self.baseUrl + str('?')
        for key, value in self.query.items():
            self.url = self.url+ f'{key}={value}&'

        self.url = self.url[0:-1]
    
    def __str__(self):
        return self.url
    
    def __repr__(self):
        return self.url
    
class Article():
    id: str | None = None # Default Value is None
    type: str
    source: str
    url: str
    title: str
    authors: List[str] | None
    topics: List[str]
    body: str | None
    publishedAt: str
    state: str | None

    def __init__(self, data:Dict) -> None:
        self.id = None
        self.type = data.get('type')
        self.source = data.get('source')
        self.url = data.get('url')
        self.title = data.get('title')
        self.authors = data.get('authors')
        self.topics = data.get('topics')
        self.body = None
        self.publishedAt = data.get('publishedAt')
        self.state = None

        self.scrape_news()
    
    def scrape_news(self) -> None:
        webPageHtml = requests.get(self.url)

        soup = BeautifulSoup(webPageHtml.text, 'html5lib')

        articleBody = [element.text for element in soup.find_all('div',{'data-component':'text-block'})]
        
        self.body = ''
        for text in  articleBody:
            self.body = self.body + text + '\n'

        return

    def __str__(self):
        value = f'Article Data\n{self.type}\n{self.topics}\n{self.source}\n{self.url}\n{self.authors}\n{self.publishedAt}\n{self.title}\n{self.body}'
        return value
    
    def getData_Dict(self) -> Dict:
        Dict = dict({"id":None, "type":self.type, "source":self.source, "url":self.url, "title":self.title, "authors":self.authors, "topics":self.topics, "body":self.body, "publishedAt":self.publishedAt, "state":None})
        return Dict
        
        

class BBC():

    SOURCE:str = "BBC"
    BASEURL:str = "https://www.bbc.com"
    BBC_Technology_News_API = "https://web-cdn.api.bbci.co.uk/xd/content-collection/092c7c94-aa9b-4933-9349-eb942b3bde77"
    BBC_ScienceHealth_News_API  = ""
    BBC_AI_NEWS_API = ""

    def __init__(self):

        self.query = {"country":"np","page":3,"size":1}

    def getArticle(self) -> Article | None:
        
        self.query['size'] = 1
        url = Url(self.BBC_Technology_News_API, self.query)
        request = requests.get(url=url)

        # request = dict(request.json())
        # request = list(request.get('data'))
        # request = request.pop()
        # Below line is the same as above three lines

        request = list(dict(request.json()).get('data')).pop()
        
        # request = list(dict(request.json()).get('data'))

        DictData = dict({"id":None, "type":None, "source":None, "url":None, "title":None, "authors":None, "topics":None, "body":None, "publishedAt":None, "state":None})
        DictData.update({"type":list([request.get('type'), request.get('subtype')]), "source":self.SOURCE, "url":self.BASEURL + request.get('path'), "title":request.get('title'), "topics":list(request.get('topics')), "publishedAt":request.get('lastPublishedAt')})
        article = Article(DictData)

        # for data in request:
        #     data = dict(data)
        #     DictData = dict({"id":None, "type":None, "source":None, "url":None, "title":None, "authors":None, "topics":None, "body":None, "publishedAt":None, "state":None})
        #     DictData.update({"type":list([data.get('type'), data.get('subtype')]), "source":self.SOURCE, "url":self.BASEURL + data.get('path'), "title":data.get('title'), "topics":list(data.get('topics')), "publishedAt":data.get('lastPublishedAt')})
        #     article = Article(DictData)

        return

    
    def getArticles(self, noOfArticles) -> List[Article] | None:
        self.query['size'] = noOfArticles
        url = Url(self.BBC_Technology_News_API, self.query)
        request = requests.get(url=url)
        request = dict(request.json()).get('data')

        listOfArticles: List[Article] | List[None] = []  

        for data in request:
            data = dict(data)
            DictData = dict({"id":None, "type":None, "source":None, "url":None, "title":None, "authors":None, "topics":None, "body":None, "publishedAt":None, "state":None})
            DictData.update({"type":list([data.get('type'), data.get('subtype')]), "source":self.SOURCE, "url":self.BASEURL + data.get('path'), "title":data.get('title'), "topics":list(data.get('topics')), "publishedAt":data.get('lastPublishedAt')})
            listOfArticles.append(Article(DictData))
        
        with open('ScrappedNews5(4).txt','w') as News:
            for article in listOfArticles:
                News.write(str(article) + '\n')

        return
    
    def getLatestArticles(self) -> List[Dict]:
        return

