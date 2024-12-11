import requests

Update_Unsummarized_API : str = "http://127.0.0.1:9200/api/update/article/status/unsummarized"
Update_Pending_API : str = "http://127.0.0.1:9200/api/update/article/status/pending"
Update_Summarized_API : str = "http://127.0.0.1:9200/api/update/article/status/summarized"

request = requests.post(url=Update_Unsummarized_API,json=dict({"id":3}))
print(request.status_code, request.content)