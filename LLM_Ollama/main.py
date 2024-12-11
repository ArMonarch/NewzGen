import datetime
import time
import queue
from enum import Enum
import threading
import sys
import requests
import json

# Database Routes
class DATABASE():
    DATABASE_BASE_API = 'http://127.0.0.1:9200'
    ADD_ARTICLE_SUMMARY = f'{DATABASE_BASE_API}/api/add/article-summary'
    UPDATE_ARTICLE_STATUS_UNSUMMARIZED = f'{DATABASE_BASE_API}/api/update/article/status/unsummarized'
    UPDATE_ARTICLE_STATUS_PENDING = f'{DATABASE_BASE_API}/api/update/article/status/pending'
    UPDATE_ARTICLE_STATUS_SUMMARIZED = f'{DATABASE_BASE_API}/api/update/article/status/summarized'
    

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
        if not ArticleQueue.empty():
            try:
                if Llm_Models.__len__() != 1:
                    print("REPORT: This feature us currently being Added.")
                else:
                    Article : dict = ArticleQueue.get()
                    Article_Id = int(Article.get('id'))
                    prompt = f''' 
                    Summarize this News Article as Stated Below:
                    Title: {Article.get('title')}
                    Body: {Article.get('body')}
                    in about one paragraph
                    '''

                    DATA = dict({"model":Llm_Models[0], "prompt":prompt, "stream": False})
                    Generated_Summary = requests.post(url=OllamaAPIs.GENERATE_SUMMARY.value, json=DATA)
                    if Generated_Summary.status_code != 200:
                        raise Exception("GENERATION ERROR: Failed to Generate Article Summary")
                    Summary : dict = dict(json.loads(Generated_Summary.content)).get("response")
                    print(f'\nFinished Summarizing {Article.get('title')}')

                    AddTo_Database = requests.post(DATABASE.ADD_ARTICLE_SUMMARY, json={"article_id":Article_Id,"llm_used":Llm_Models[0], "generated_summary":str(Summary)})
                    if AddTo_Database.status_code != 201:
                        raise Exception("FATAL ERROR")
                    print(f'Added Summary of Article Title:{Article.get('title')} to Database \n')

                    Update_Status_Summarized = requests.post(DATABASE.UPDATE_ARTICLE_STATUS_SUMMARIZED, json={"id": Article_Id})
                    if Update_Status_Summarized.status_code != 201:
                        raise Exception("UPDATE ERROR")
                    
                    ArticleQueue.task_done()
            
            except Exception as e:
                print(str(e))
        
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
                
        Thread = threading.Thread(target=Article_Summarization_Worker, args=(ArticleQueue, StopEvent))
        Thread.start()

        while True:
            requested = requests.get(f'{DATABASE.DATABASE_BASE_API}/api/get/unsummarized/article')

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
                
                if "video" in Article.get('type'):
                    Update_Status_Pending = requests.post(DATABASE.UPDATE_ARTICLE_STATUS_PENDING, json={"id": Article.get('id')})
                    continue

                ArticleQueue.put(Article)
                Update_Status_Pending = requests.post(DATABASE.UPDATE_ARTICLE_STATUS_PENDING, json={"id": Article.get('id')})
                print(f'\nREPORT: Added Article ID:{Article.get('id')}:{Article.get('title')} to Article Queue for summarization')

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
        Thread.join()
        while not ArticleQueue.empty():
            Reroll_Status_Unsummarized = requests.post(DATABASE.UPDATE_ARTICLE_STATUS_UNSUMMARIZED, json={"id":dict(ArticleQueue.get()).get('id')})
            print(f'Unsummarized One Article')