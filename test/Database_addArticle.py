import requests

DATA : dict = {
    'id': 150,
    'type':['article', 'news'],
    'authors':None,
    'title':'Test',
    'topics':['Article', 'News'],
    'body':'Lorem Ipsum',
    'publisheddate':'asdadad',
    'source':'BBC',
    'url':'bbc.com',
    'summarized_status':False
}

request = requests.post('http://127.0.0.1:9200/api/add/article',json=DATA)
print(request.status_code, request.text)