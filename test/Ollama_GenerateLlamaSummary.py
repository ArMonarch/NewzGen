import requests

requested = requests.post('http://127.0.0.1:9100/api/llama/generate/summary')

print(requested.status_code)
print(requested.text)