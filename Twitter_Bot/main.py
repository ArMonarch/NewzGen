import os
import json
# import redis
import requests
from typing import Self
from tweepy import Client, TooManyRequests
from flask import Flask, request

# init the redis redis_database
# redis_database = redis.Redis(host="localhost", port=6379, decode_responses=True)

# for Newz_gen account
API_Key = os.environ.get("API_KEY")
API_Key_Secret = os.environ.get("API_KEY_SECRET")
Access_Token = os.environ.get("ACCESS_TOKEN")
Access_Token_Secret = os.environ.get("ACCESS_TOKEN_SECRET")

# init flask app
app = Flask(__name__)

# init the twitter bot client for handeling message posting
client = Client(consumer_key=API_Key, consumer_secret=API_Key_Secret, access_token=Access_Token, access_token_secret=Access_Token_Secret)

# class to represent summary
class Summary:
    def __init__(self, id: int, article_id: int, llm_used: str, generated_summary: str) -> None:
        self.summary_id = id
        self.article_id = article_id
        self.llm_used = llm_used
        self.generated_summary = generated_summary

    @classmethod
    def new(cls, value: dict) -> Self:
        if value["id"] != None and value["article_id"] != None and value["llm_used"] != None and value["generated_summary"] != None:
            return cls(value["id"] != None, value["article_id"] != None, value["llm_used"] != None, value["generated_summary"])
        else:
            return cls(-1,-1,"","")

# function to create the twitter post by formatting the string
def format_summary(summary: Summary) -> str:
    # check if this summary is valid, id id == -1 it is invalid
    if summary.summary_id == -1:
        return "Invalid"

    # remove ** form the generated summary
    generated_summary_list: list = [lines.replace("*", "") for lines in summary.generated_summary.splitlines() if lines != ""]

    # remove the dentene containing consise of summary substring as it is not needed
    if "concise" in generated_summary_list[0] or "summary" in generated_summary_list[0]:
        generated_summary_list.pop(0)

    return "\n".join(generated_summary_list)

# Database routes
class Database:
    DATABASE_BASE_API = "http://127.0.0.1:9200"
    GET_SUMMARY = "{}/api/get/article-summary".format(DATABASE_BASE_API)

@app.route("/api/post/summary", methods=["GET"])
def post_summary():
    try:
        if request.method != "GET":
            raise Exception("METHOD ERR: Route only supports GET method")

        summary_id: int = request.args.get("summary_id", default=-1, type=int)

        if summary_id == -1:
            raise Exception("Query Err: Required summary_id as a query")

        payload = {"summary_id": summary_id}
        response = requests.post(Database.GET_SUMMARY, json=payload)
        if response.status_code == 404:
            raise Exception("Request Err: Data Not Found")

        if response.status_code != 201:
            raise Exception("Request Err: Failed to get the article summary")

        summary = Summary.new(json.loads(response.content))
        formatted_summary = format_summary(summary)

        if formatted_summary.__len__() <= 280:
            client.create_tweet(text=formatted_summary)
        else:
            raise Exception(f'Summary Length More than 280 Words: Summary Len: formatted_summary.__len__()')

        return (formatted_summary, 201)

    except TooManyRequests as Err:
        print("Twitter Post Creating Limit Reached")
        return (str(Err), 429)

    except Exception as err:
        print("[Error] %s" % str(err))
        return (str(err), 401)

if __name__ == "__main__":
    app.run(port=9300, debug=True, load_dotenv=True)
