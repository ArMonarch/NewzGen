import datetime
import json
from os import wait
import queue
import threading
import time
from typing import Self

import requests

# Database Routes
class DATABASE():
    DATABASE_BASE_API = 'http://127.0.0.1:9200'
    ADD_ARTICLE_SUMMARY = f'{DATABASE_BASE_API}/api/add/article-summary'
    GET_UNSUMMARIZED_ARTICLE = f'{DATABASE_BASE_API}/api/get/unsummarized/article'
    UPDATE_ARTICLE_STATUS_UNSUMMARIZED = f'{DATABASE_BASE_API}/api/update/article/status/unsummarized'
    UPDATE_ARTICLE_STATUS_PENDING = f'{DATABASE_BASE_API}/api/update/article/status/pending'
    UPDATE_ARTICLE_STATUS_SUMMARIZED = f'{DATABASE_BASE_API}/api/update/article/status/summarized'

# Ollama APIs
class OllamaAPIs():
    BASE_API = "http://127.0.0.1:11434"
    GET_LLM_MODELS = f'{BASE_API}/api/tags'
    CREATE_MODEL = f'{BASE_API}/api/create' 
    GENERATE_SUMMARY = f'{BASE_API}/api/generate'

# list of needed LLM & available LLM
NEEDED_LLM_MODELS = ["llama3.1:latest", "llama3.2:latest"] # Either is fine
Available_Models: list = list()

# Our Summarization Model Name
SUMMARY_MODEL = "summarization_armonarch_v0.2"

# check for availabel LLM models locally
def check_for_needed_llms() -> bool:
    try:
        # from  local ollama get available_models
        response = requests.get(OllamaAPIs.GET_LLM_MODELS)
        if response.status_code != 200:
            raise Exception("REQUEST ERROR: Err while fetching Available LLM models ( Check if Ollama is running properly )")

        # Check if NEEDED_LLM_MODELS are locally available
        response_json: dict = json.loads(response.content)
        available_models: list = list(response_json["models"]) if response_json["models"] != None else list()

        # store all locally available models in Available_Models as return true
        model_available: bool = False
        for model in available_models:
            if model["name"] in NEEDED_LLM_MODELS:
                Available_Models.append(model["name"])
                model_available = True
        # prompt user if No Needed LLM found locally
        if not model_available:
            print("No Needed LLM found Locally")

        return model_available

    except Exception as err:
        print(str(err))
        return False

# create summarization model at runtime
def create_model( model_name: str) -> bool:
    # created LLM model name & modelfile
    # edit this to tune model summarization capability
    model = SUMMARY_MODEL
    modelfile = 'FROM %s\nSYSTEM You are a professional news summarizer. Your task is to distill long and complex news articles into concise, engaging, and accurate summaries while preserving the main points and key details. Ensure the tone matches the content type (formal for hard news, casual for lighter stories) and include any critical context needed for a clear understanding.' % model_name

    try:
        payload: dict = {"model": f'{model}', "modelfile": modelfile}
        with requests.post(url=OllamaAPIs.CREATE_MODEL, json=payload, stream=True) as response:
            # check if the response status code is OK
            response.raise_for_status()

            # iterate over the response line by line
            for line in response.iter_lines():
                #skip empty line
                if line:
                    # parse line as json 
                    json_data = json.loads(line)
                    print(json_data)
        return True

    except Exception as err:
        print(str(err))
        return False

def __init_ollama__() -> bool:

    # check for locally available LLM models and update the Available_Models list
    if check_for_needed_llms():
        if NEEDED_LLM_MODELS[1] in Available_Models:
            return create_model(NEEDED_LLM_MODELS[1])
        elif NEEDED_LLM_MODELS[0] in Available_Models:
            return create_model(NEEDED_LLM_MODELS[0])
    return False

class Article:
    def __init__(self, articel_id:int, article_title:str, article_type:str, article_topics:str, article_body:str) -> None:
        self.articel_id: int = articel_id
        self.article_title: str = article_title
        self.article_type:str = article_type
        self.article_topics:str = article_topics
        self.article_body:str = article_body

    # check if class  was init as null
    def null_init(self) -> bool:
        if self.articel_id != -1:
            return False
        # if null init return False
        return True

    @classmethod
    def default(cls) -> Self:
        return cls(-1,"default","default","default","default")

    @classmethod
    def new(cls, value:dict) -> Self:
        # init this class with dict containing required values
        if value['article_id'] != None and value['article_title'] != None and value['article_type'] and value['article_topics'] != None and value['article_body'] != None:
            return cls(value['article_id'] ,value['article_title'] ,value['article_type'], value['article_topics'], value['article_body'])

        raise Exception("Some Value missing in article_id, article_title, article_type, article_topics, article_body'")

    @classmethod
    def null(cls) -> Self:
        return cls(-1, "None", "None", "None", "None")

# function to get unsummarized articel
def get_unsummarized_article() -> Article:
    try:
        response = requests.get(DATABASE.GET_UNSUMMARIZED_ARTICLE)
        # check for status error codes and raise exception
        if response.status_code != 201 and response.status_code != 404:
            raise Exception("REQUEST ERROR: Failed to fetch unsummarized article")
        # for 404 (aka No unnsummarized article left)
        if response.status_code == 404:
            return Article.null()

        #parse response as json
        response_json = json.loads(response.content)

        # check if the article is an video article 
        # if yes return Article.null()
        if "video" in list(response_json["type"]):
            return Article.null()

        article: dict = {
            "article_id": response_json['id'] if response_json['id'] != None else -1,
            "article_title": response_json['title'] if response_json['title'] != None else "",
            "article_type": ",".join(response_json['type']) if response_json['type'] != None else "",
            "article_topics": ",".join(response_json['topics']) if response_json['topics'] != None else "",
            "article_body": response_json['body'] if response_json['body'] != None else ""
        }
        return Article.new(article)

    except Exception as err:
        print(str(err))
        return Article.null()

def update_article_status_unsummarized(article: Article) -> bool:
    try:
        update_status = requests.post(DATABASE.UPDATE_ARTICLE_STATUS_UNSUMMARIZED, json={"id": article.articel_id})
        if update_status.status_code != 201:
            raise Exception("REQUEST ERROR: Err while updating Article status, Article_Id:%d" % article.articel_id)
        return True
    except:
        return False

def update_article_status_pending(article: Article) -> bool:
    try:
        update_status = requests.post(DATABASE.UPDATE_ARTICLE_STATUS_PENDING, json={"id": article.articel_id})
        if update_status.status_code != 201:
            raise Exception("REQUEST ERROR: Err while updating Article status, Article_Id:%d" % article.articel_id)
        return True
    except:
        return False

def update_article_status_summarized(article: Article) -> bool:
    try:
        update_status = requests.post(DATABASE.UPDATE_ARTICLE_STATUS_SUMMARIZED, json={"id": article.articel_id})
        if update_status.status_code != 201:
            raise Exception("REQUEST ERROR: Err while updating Article status, Article_Id:%d" % article.articel_id)
        return True
    except Exception as err:
        print(str(err))
        return False

# TODO: Complete this Worker Function
def article_summary_worker(article_queue: queue.Queue, stop_event: threading.Event):
    while not stop_event.is_set():
        if not article_queue.empty():
            try:
                pass
            except:
                pass
        # if queue is empty wait for 1 seconds
        time.sleep(1)

if __name__ == "__main__":

    # create Article Summarization Worker Thread with Created Summarization Model
    # Init Article queue
    article_queue: queue.Queue[Article] = queue.Queue()

    # Threading event flag to stop worker thread if any error occures
    stop_event = threading.Event()

    # run the article summary worker thread with args as article queue and stop event
    Thread = threading.Thread(target=article_summary_worker, args=(article_queue, stop_event))

    try:
        Thread.start()
        # init ollama with  created summarization LLM Model
        if __init_ollama__():
            # start queueing articles for summarization
            while True:
                # if queue size > 30 wait 5sec and continue
                if not article_queue._qsize() < int(30):
                    print("QUEUE: Queue full trying after 5sec")
                    time.sleep(1.0 * 5)
                    continue

                unsummarized_article: Article = get_unsummarized_article()
                if unsummarized_article.null_init():
                    time.sleep(1.0 * 30) # sleep for 60 sec as mostly there is no unsummarized_article OR got video Article and start next iteration
                    continue

                # Not needed due to error handeling in update_article_status_pending function
                # it directly jumps to except portion
                # change the unsummarized_article status to pending
                while not update_article_status_pending(unsummarized_article):
                    time.sleep(1.0) # may be due to ... so wait 0.5 sec

                article_queue.put(unsummarized_article)

                time.sleep(1.0)
        else:
            raise Exception("Error while initializing Ollama with summarization model")

    except KeyboardInterrupt:
        # for keyboard interrupt stop summarizer after completing current article and execute final  statements
        stop_event.set()
        print("Stopping Worker Thread Due To Keyboard Interrupt")

    except Exception as err:
        print(str(err))

    finally:
        Thread.join()
        while not article_queue.empty():
            article: Article = article_queue.get()
            if not update_article_status_unsummarized(article):
                print("Update Error: failed to update Article with ID: %d status to unsummarized" % article.articel_id)
                article_queue.put(article)
            print("Updated Article of ID: %d status to unsummarized" % article.articel_id)
