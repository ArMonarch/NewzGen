import requests

DATA : dict = {
    'type':['Article', 'News'],
    'authors':None,
    'title':'Test',
    'topics':['Article', 'News'],
    'body':'asdasdasdadadadsad',
    'publisheddate':'asdadad',
    'source':'adadadadadasdadas',
    'url':'Nothing',
    'summarized_status':False
}

request = requests.post('http://127.0.0.1:9200/api/add/article',json=DATA)
print(request.status_code)