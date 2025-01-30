import time
import queue
import schedule
import threading
# import os
# import subprocess
# from datetime import datetime
import requests
import json
from typing import Dict, List

# this code contains the main loop of the progeam that regulates all the sub server

# Create a queue to hold jobs
Queue = queue.Queue()

# This event will be used to signal the worker thread to stop
stopEvent = threading.Event()

# TODO: Start all the modules from this file
# runnung this file automatically starts Database, News_Scrapper, LLM_Ollama, Twitter_Bot as Thread

# # Get current working directory
# CURRENT_DIRECTORY = os.getcwd()

# # run Database Server
# DATABASE_DIRECTORY = os.path.join(CURRENT_DIRECTORY,'SQLite_Database_Server')

# def Database_Server():
#     EXECUTABLE = os.path.join(DATABASE_DIRECTORY,'main.py')
#     print(EXECUTABLE)
#     subprocess.run(f'{CURRENT_DIRECTORY}/venv/bin/python {EXECUTABLE}')

# DATABASE_SERVER = threading.Thread(target=Database_Server())
# DATABASE_SERVER.start()

class Newz_Server():
    NEWZ_SCRAPPER_SERVER = "http://127.0.0.1:9400"

    def __init__(self):
        pass

    def getArticle(self, topic) -> Dict:
        API = f'{self.NEWZ_SCRAPPER_SERVER}/api/bbc/get/article'
        request = requests.get(url=API, params={'topic':topic})
        if request.status_code != 201:
            raise Exception('REQUESTS ERROR: Failed to Fetch Data')
        DATA : Dict = json.loads(request.content)
        return DATA

    def getArticles(self, topic, size : int = 1) -> List[Dict]:
        API = f'{self.NEWZ_SCRAPPER_SERVER}/api/bbc/get/articles'
        request = requests.get(url=API, params={'topic':topic, 'size':size})
        if request.status_code != 201:
            raise Exception('REQUESTS ERROR: Failed to Fetch Data')
        DATA = json.loads(request.content)
        return DATA
    
    def getArticleId(self,articleNo, topic) -> dict:
        API = f'{self.NEWZ_SCRAPPER_SERVER}/api/bbc/get/article'
        request = requests.get(url=API, params={'page':articleNo,'topic':topic})
        if request.status_code != 201:
            raise Exception('REQUESTS ERROR: Failed to Fetch Data')
        DATA : dict = json.loads(request.content)
        return DATA
    
def insert_Article(DATA : dict) -> None :
    API = f'http://127.0.0.1:9200/api/add/article'
    request = requests.post(url=API, json=DATA)
    if request.status_code != 201:
        raise Exception('REQUESTS ERROR: Failed to Post Data')
    return

def find_Article(title : str) -> (dict | None) :
    API = f'http://127.0.0.1:9200/api/get/article'
    request = requests.post(url=API, json={'title':title})

    if request.status_code == 404:
        return None
    elif request.status_code != 201:
        raise Exception('REQUESTS ERROR: Failed to Get Article')

    return json.loads(request.content)

def database_isEmpty() -> bool:
    API = f'http://127.0.0.1:9200/api/database/empty'
    request = requests.get(API)
    if request.status_code != 201:
        raise Exception('REQUESTS ERROR: Failed to Check Database Status')
    status = False if str(request.text) != 'True' else True
    return status

# TOPICS : list[str] = ["us-canada", "uk", "africa", "asia", "australia", "europe", "latin-america", "middle-east", "science-health", "technology", "ai-news"]
# Reduce the topics for scraping
TOPICS : list[str] = ["us-canada", "uk", "asia", "australia", "europe", "science-health", "technology"]

def main():
    News = Newz_Server()
    Article : dict

    for topic in TOPICS:
        for i in range(0,99):
            try:
                Article = News.getArticleId(articleNo=i, topic=topic)
                article_title: str = str(Article.get("title"))

                print(f'Got {topic} News, Article : {Article.get('title')}, Number ID {i+1}')
                if not find_Article(article_title):
                    insert_Article(Article)
                    print(f'Inserted {topic} News, Number ID {i+1}')

                else:
                    break

            except Exception as e:
                print(str(e))

    return

def WorkerMain(Queue: queue.Queue, StopEvent: threading.Event):
    while not StopEvent.is_set():
        if not Queue.empty():
            Process = Queue.get()
            Process()
            Queue.task_done()
        time.sleep(0.5)

if __name__ == "__main__":

    try:
        DATABASE_EMPTY : bool = database_isEmpty()
        # if database is empty populate the database with 10 articles
        if DATABASE_EMPTY:
            Articles = Newz_Server().getArticles(topic="technology",size=100)
            for Article in Articles:
                insert_Article(Article)
            print("Finished populating the database with articles")

    except Exception as e:
        print(str(e))

    Queue.put(main)
    schedule.every(30).minutes.do(Queue.put,main)

    Thread = threading.Thread(target=WorkerMain, args=(Queue, stopEvent))
    Thread.start()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping the worker thread due to user interrupt...")
        stopEvent.set()

    except:
        print('Stoping Due to unknown error')
        stopEvent.set()

    finally:
        Thread.join()
