import requests

request = requests.post('http://127.0.0.1:9200/api/get/article',json={"articleId":"1"})

for key, value in dict(request.json()).items():
    print(f'{key}:{type(value)}')
    print(f'{key}:{value}\n')

# Expected Values

# authors:<class 'NoneType'>
# body:<class 'str'>
# id:<class 'int'>
# publishedDate:<class 'str'>
# source:<class 'str'>
# summarized_status:<class 'bool'>
# title:<class 'str'>
# topics:<class 'list'>
# type:<class 'list'>
# url:<class 'str'>