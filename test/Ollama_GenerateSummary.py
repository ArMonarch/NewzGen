import requests

request = requests.post('http://127.0.0.1:9100/api/generate/summary')
print(request.json())