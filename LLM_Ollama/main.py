import datetime
import time
import queue
from enum import Enum
import threading
import sys
import requests
import json

# Database Route
DATABASE_API = 'http://127.0.0.1:9200'

# Enum Class for Ollama APIs
class OllamaAPIs(Enum):
    BASE_API = "http://127.0.0.1:11434"
    GET_LLM_MODELS = f'{BASE_API}/api/tags'
    GENERATE_SUMMARY = f'{BASE_API}/api/generate'

# Needed LLM Models
NEEDED_LLM_MODELS = ["llama3.1:latest", "llama3.2:latest", "mistral:latest", "gemma2:9b"]

# LLM_Models that are in Needed LLM Models and are available locally
Llm_Models = list()

# Queue to holds jobs
Queue = queue.Queue()

# Article Queue
ArticleQueue = queue.Queue()

# Event flag
StopEvent = threading.Event()

def Article_Summarization_Worker( ArticleQueue: queue.Queue, StopEvent: threading.Event):
    while not StopEvent.is_set():
        if not Queue.empty():
            if Llm_Models.__len__() != 1:
                print("REPORT: This feature us currently being Added.")
            else:
                Article : dict = ArticleQueue.get()
                prompt = f''' 
                Summarize this News Article as Stated Below:
                Title: {Article.get('title')}
                Type: {Article.get('type')}
                Topics: {Article.get('topics')}
                Body: {Article.get('body')}
                '''
                DATA = dict({"model":Llm_Models[0], "prompt":prompt, "format": "json", "stream": False})
                Generated_Summary = requests.post(url=OllamaAPIs.GENERATE_SUMMARY.value, json=DATA)
                if Generated_Summary.status_code != 200:
                    raise Exception("GENERATION ERROR: Failed to Generate Article Summary")
                Summary : dict = dict(json.loads(Generated_Summary.content))
        
        time.sleep(1)

if __name__ == "__main__":
    try:

        # check if the LLM_MODELS are available if not raise exceptions
        request = requests.get(OllamaAPIs.GET_LLM_MODELS.value)

        if request.status_code != 200:
            raise Exception("REQUEST ERROR: Cannot get LLM models from Ollama server. Is Ollama server running?")
        
        Ollama_response = dict(json.loads(request.content))
        if list(Ollama_response.get('models')).__len__() == 0:            
            print("REPORT: No LLM Model found Locally ...Exiting")
            sys.exit(1)

        for model in list(Ollama_response.get('models')):
            Model_Name = dict(model).get("name")
            if Model_Name != None:
                if Model_Name in NEEDED_LLM_MODELS:
                    print(f'REPORT: found {Model_Name} available Locally')
                    Llm_Models.append(Model_Name)
                else:
                    print(f'REPORT: Not found {Model_Name} available Locally')
                    
                    # TODO: Feature
                    # Do you like to pull the specified Model. (y/n)
                    # if Y Use ollama api for pulling model
                
        threading.Thread(group=None, target=Article_Summarization_Worker, args=(ArticleQueue, StopEvent))

        while True:
            requested = requests.get(f'{DATABASE_API}/api/get/unsummarized/article')

            if requested.status_code != 201 and requested.status_code != 404:
                # There was error fetching the unsummarized news.
                raise Exception("REQUEST ERROR: Error when fetching the articles")
            
            if requested.status_code == 404:
                # All articles are already summarized so wait 1 Mins for any new articles
                time.sleep(1 * 60)
                continue
            
            DATA = dict(json.loads(requested.content))
            
            Article = dict({"id":DATA.get('id'), "title":DATA.get('title'), "type":DATA.get('type'), "topics":DATA.get('topics') ,"body":DATA.get('body')})
            del DATA
            
            if ArticleQueue._qsize() <= 30:
                ArticleQueue.put(Article)
                print(f'REPORT: Added Article ID:{Article.get('id')} Title:{Article.get('title')} to Article Queue for summarization')
            else:
                time.sleep(1 * 30) # sleep for 30 seconds and check again
                continue
            
            # wait until the summarization is finished

            # After finishing a work for Article summarization sleep for 1 sec
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping the worker thread due to user interrupt...")
        StopEvent.set()

    except Exception as e:
        print(str(e))

    finally:
        pass