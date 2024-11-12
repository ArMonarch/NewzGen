import time
import queue
import schedule
import threading
import os
import subprocess
import requests
import json
from typing import Dict, List

# this code contains the main loop of the progeam that regulates all the sub server

# Create a queue to hold jobs
Queue = queue.Queue(maxsize=20)

# This event will be used to signal the worker thread to stop
stopEvent = threading.Event()

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
    NEWZ_SCRAPPER_SERVER = 'http://127.0.0.1:9400'

    def __init__(self):
        pass

    def getArticle(self) -> Dict:
        API = f'{self.NEWZ_SCRAPPER_SERVER}/api/bbc/get/article'
        request = requests.get(url=API, params={'topic':'unknown'})
        if request.status_code != 201:
            raise Exception('REQUESTS ERROR: Failed to Fetch Data')
        DATA : Dict = json.loads(request.content)
        return DATA
        
    def getArticles(self, size : int = 1) -> List[Dict]:
        API = f'{self.NEWZ_SCRAPPER_SERVER}/api/bbc/get/articles'
        request = requests.get(url=API, params={'topic':'unknown', 'size':size})
        if request.status_code != 201:
            raise Exception('REQUESTS ERROR: Failed to Fetch Data')
        DATA : Dict = json.loads(request.content)
        return DATA
    
def insert_Article(DATA : dict) -> None :
    API = f'http://127.0.0.1:9200/api/add/article'
    request = requests.post(url=API, json=DATA)
    if request.status_code != 201:
        raise Exception('REQUESTS ERROR: Failed to Post Data')
    return

def find_Article(title : str) -> dict :
    API = f'http://127.0.0.1:9200/api/get/article'
    request = requests.post(url=API, json={'title':title})
    print(request.content)
    pass

# def find_Article(articleId : int) -> dict:
#     API = f'http://127.0.0.1:9200/api/get/article'
#     request = requests.post(url=API, json={'articleId':articleId})
#     pass


def main():
    
    # job1 : Get 1 article and check if the article is already in the database
    # Article : dict = Newz_Server().getArticle()

    find_Article(title="'I was moderating hundreds of horrific and traumatising videos'")

    # insert_Article(Article)

    # job2 : Get another 2 article and check if the article is already in the database

    return

def WorkerMain(Queue: queue.Queue, StopEvent: threading.Event):
    while not StopEvent.is_set():
        if not Queue.empty():
            Process = Queue.get()
            Process()
            Queue.task_done()
        time.sleep(0.1)

if __name__ == "__main__":

    main()
    schedule.every(5).seconds.do(Queue.put,main)

    Thread = threading.Thread(target=WorkerMain, args=(Queue, stopEvent))
    Thread.start()

    try:
        while True:
            schedule.run_pending()
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nStopping the worker thread due to user interrupt...")
        stopEvent.set()

    except:
        print('Stoping Due to unknown error')
        stopEvent.set()

    finally:
        Thread.join()