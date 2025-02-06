import time
import queue
import schedule
import threading
import requests
import json
from typing import Dict, Callable

# Reduce the topics for scraping
TOPICS : list[str] = ["us-canada", "uk", "asia", "australia", "europe", "science-health", "technology"]

class RequestError(Exception):
    def __init__(self, message: str) -> None:
        super.__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f'Request Error: {self.message}'

class Newz_Gen():
    NEWZ_SCRAPPER_BASEAPI = 'http://127.0.0.1:9400'

    def __init__(self):
        pass

    def get_article(self, topic = "technology") -> Dict | None :
        # assert topic is str && in TOPICS
        assert isinstance(topic, str)
        assert topic in TOPICS

        GET_ARTICLE_API = f"{self.NEWZ_SCRAPPER_BASEAPI}/api/bbc/get/articles"
        try:
            response = requests.get(url=GET_ARTICLE_API, params={"topic": topic, "size": 1})
            if response.status_code != 201:
                raise RequestError("Failed to get latest Article")
            return json.loads(response.content)

        except (RequestError, Exception) as Err:
            print(f'{str(Err)}')
            return None

    def get_articles(self,size: int, topic: str = "technology") -> Dict | None :

        # assert topic is str && in TOPICS
        assert isinstance(topic, str)
        assert topic in TOPICS

        # assert size isinstance of int && size > 1 & size < 100
        assert isinstance(size, int)
        assert size < 100 and size > 0

        GET_ARTICLES_API = f"{self.NEWZ_SCRAPPER_BASEAPI}/api/bbc/get/articles"
        try:
            response = requests.get(url=GET_ARTICLES_API, params={"topic":topic, "size": size})
            if response.status_code != 201:
                raise RequestError("Failed to get Latest Articles")
            return json.loads(response.content)

        except (RequestError, Exception) as Err:
            print(f'{str(Err)}')
            return None

    def get_article_id(self, topic: str, article_no: int)-> Dict | None :

        # assert topic is str && in TOPICS
        assert isinstance(topic, str)
        assert topic in TOPICS

        # assert article_no isinstance of int && article_no > 1 & article_no < 100
        assert isinstance(article_no, int)
        assert article_no < 100 and article_no >= 0

        GET_ARTICLE_WITH_ID_API = f'{self.NEWZ_SCRAPPER_BASEAPI}/api/bbc/get/article'
        try:
            response = requests.get(url=GET_ARTICLE_WITH_ID_API, params={"topic": topic, "page": article_no, "size": 1})
            if response.status_code != 201:
                raise RequestError(f'Failed to get Article of ID {article_no}')
            return json.loads(response.content)

        except (RequestError, Exception) as Err:
            print(f'{str(Err)}')
            return None

class Database():
    DATABASE_BASEAPI = "http://127.0.0.1:9200"
    DATABASE_INSERT_ARTICLE = f'{DATABASE_BASEAPI}/api/add/article'
    DATABASE_FIND_ARTICLE = f'{DATABASE_BASEAPI}/api/get/article'
    DATABASE_EMPTY = f'{DATABASE_BASEAPI}/api/database/empty'

    def __init__(self) -> None:
        pass

    def empty(self) -> bool | None :

        try:
            response = requests.get(url=self.DATABASE_EMPTY)
            if response.status_code != 201:
                raise RequestError("Failed to check Databse Status")
            status : bool = False if str(response.text) != "True" else True
            return status
        except (RequestError, Exception):
            return None

    def find_article(self, article_title: str) -> bool | None :

        # assert title is str
        assert isinstance(article_title, str)

        try:
            response = requests.post(url=self.DATABASE_FIND_ARTICLE, json={"title": article_title})
            if response.status_code != 201 and response.status_code != 404:
                raise RequestError("Failed to Find Article in Database")
            if response.status_code == 404:
                return False
            else:
                return True

        except (RequestError, Exception) as Err:
            print(f'{str(Err)}')
            return None

    def insert_article(self, Article: Dict) -> bool | None :
 
        # assert that the Article is Dict
        assert isinstance(Article, Dict)
        # TODO: assert the Article contatin (title, body, ...)
        assert True

        try:
            response = requests.post(url=self.DATABASE_INSERT_ARTICLE, json=Article)
            if response.status_code != 201:
                raise RequestError("Failed to Post Article")
            return True
        except (RequestError, Exception) as Err:
            print(f'{str(Err)}')
            return None

def main() -> None:
    for topic in TOPICS:
        # iterate through 0 to  100
        for index in range(0,100):
            try:
                found:bool = False

                while True:
                    Article = Newz_Gen().get_article_id(topic=topic, article_no=index)
                    if Article == None:
                        print("Article Err: Wait 3 Sec and Trying ...")
                        time.sleep(1 * 3)
                        continue

                    # assert that article is not none
                    assert isinstance(Article, Dict), "Is the News_Scrapper Server Running"

                    print(f'Got {topic} News, Article : {Article["title"]}, Number ID {index+1}')

                    article_found = Database().find_article(Article["title"])
                    if article_found == None:
                        print("Database Err: Wait 3 Sec and Trying...")
                        time.sleep(1 * 3)
                        continue

                    # assert article_found is bool
                    assert isinstance(article_found, bool), "Is the Database Server Running?"
                    if not article_found:
                        if Database().insert_article(Article) == None:
                            print("Wait 3 Sec and Trying...")
                            time.sleep(1 * 3)
                            continue
                        print(f'Inserted {topic} News, Article : {Article["title"]}, Number ID {index+1}')
                    else:
                        found = True

                    break
                # exit range loop if articel is found in database else insert into databas
                # We dont need older news
                if found:
                    break

            except Exception:
                pass

# Run the Main  job every 10 Mins

# Create a queue to hold jobs
Queue: queue.Queue[Callable] = queue.Queue()

# This event will be used to signal the worker thread to stop
stopEvent = threading.Event()

def queue_worker(Queue: queue.Queue[Callable], stop_event: threading.Event):
    while not stop_event.is_set():
        while not Queue.empty():
            main_function = Queue.get()
            main_function()
            Queue.task_done()
        time.sleep(1 * 0.5)

if __name__ == "__main__":
    # schedule main too queue every 10 Mins
    schedule.every(1).seconds.do(Queue.put, main)

    # start the queue_worker thread
    Queue_Worker_Thread = threading.Thread(target=queue_worker, args=(Queue, stopEvent))
    Queue_Worker_Thread.start()

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
        Queue_Worker_Thread.join()
