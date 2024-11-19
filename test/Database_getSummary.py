import requests

requested = requests.post('http://127.0.0.1:9200/api/get/article-summary', json={'summary_id':25})

requested = requested.json()

for key, values in dict(requested).items():
    print(f'{key}:{type(values)}')
    print(f'{key}:{values}')