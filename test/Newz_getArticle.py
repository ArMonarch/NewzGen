import requests

request = requests.get('http://127.0.0.1:9400/api/bbc/get/article',params={'page':'9','topic':'unknown'})

print(request.status_code)

for key,values in dict(request.json()).items():
    print(f'{key}:{type(values)}')
    print(f'{key}:{values}\n')