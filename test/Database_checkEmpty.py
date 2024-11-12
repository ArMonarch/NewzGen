import requests

request = requests.get('http://127.0.0.1:9200/api/database/empty')

print(request.content)