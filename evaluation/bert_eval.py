from bert_score import BERTScorer

import requests
import json

from torch import Tensor

article_range = range(1,70)

# 0_index = summarization without options
# 1_index = suummarization with options
# 2_index = llama3.1
# 3_index = llama3.2
# 4_index = without options
# 5_index = with options

class Database:
    GET_ARTICLE = "http://127.0.0.1:9200/api/get/article"
    GET_ARTICLE_SUMMARY = "http://127.0.0.1:9200/api/get/eval/article-summary"

def get_article(article_id: int) -> (str | None):
    try:
        response = requests.post(Database.GET_ARTICLE, json={"article_id": article_id})

        if response.status_code != 201:
            raise Exception("Request Err: Failed to fetch article")

        article = json.loads(response.content)
        if "video" in  article["type"]:
            return None
        return article["body"]

    except Exception:
        return None

def get_article_summaries(article_id: int) -> (dict | None):
    try:
        response = requests.get(Database.GET_ARTICLE_SUMMARY, params={"article_id": article_id})
        if response.status_code != 201:
            raise Exception("Request Err: Failed to fetch article")

        summaries: dict = dict(response.json())
        return summaries["article_summary"]

    except Exception:
        return None

def average(array: list) -> float:
    assert isinstance(array, list)

    len: int = array.__len__()
    sum: float = 0.0
    for value in array:
        sum += value
    return sum/len

def get_average(heading: str, p1: tuple[Tensor,Tensor,Tensor] | str | Tensor, r1: tuple[Tensor,Tensor,Tensor] | str | Tensor, f1: tuple[Tensor,Tensor,Tensor] | str | Tensor) -> None :

    assert isinstance(p1, Tensor)
    assert isinstance(r1, Tensor)
    assert isinstance(f1, Tensor)

    print(f"\n{heading}")

    p1_average = average(p1.tolist())
    r1_average = average(r1.tolist())
    f1_average = average(f1.tolist())

    print(f"P1: {p1_average}, R1: {r1_average}, F1: {f1_average}")

def print_bert_average() -> None:
    # init all articles along with respective summaries as dict
    articles: list[str] = []

    llama31_summary: list = []
    llama31_without_summary: list = []
    llama31_with_summary: list = []

    llama32_summary: list = []
    llama32_without_summary: list = []
    llama32_with_summary: list = []

    for article_id in article_range:
        # get article & article summary

        article = get_article(article_id)
        if article == None:
            continue

        articles.append(article)

        summaries = get_article_summaries(article_id)
        if summaries == None:
            continue

        llama31_summary.append(summaries["llama3.1"])
        llama32_summary.append(summaries["llama3.2"])

        llama31_without_summary.append(summaries["llama3.1_without"])
        llama32_without_summary.append(summaries["llama3.2_without"])

        llama31_with_summary.append(summaries["llama3.1_with"])
        llama32_with_summary.append(summaries["llama3.2_with"])

    #print average article length
    total_length = 0
    for value in articles:
        total_length += value.__len__()
    print("Average Word Count: ", total_length / articles.__len__())

    # get bert score average
    scorer = BERTScorer(lang="en")

    # llama3.1 average bert score
    P1, R1, F1 = scorer.score(llama31_summary, articles)
    get_average(heading_list[0], P1, R1, F1)

    # llama3.2 average bert score
    P1, R1, F1 = scorer.score(llama32_summary, articles)
    get_average(heading_list[1], P1, R1, F1)

    # llama3.1 without options bert score
    P1, R1, F1 = scorer.score(llama31_without_summary, articles)
    get_average(heading_list[2], P1, R1, F1)

    # llama3.2 without options bert socre
    P1, R1, F1 = scorer.score(llama32_without_summary, articles)
    get_average(heading_list[3], P1, R1, F1)

    # llama3.1 with options bert score
    P1, R1, F1 = scorer.score(llama31_with_summary, articles)
    get_average(heading_list[4], P1, R1, F1)

    # llama3.2 with options bert score
    P1, R1, F1 = scorer.score(llama32_with_summary, articles)
    get_average(heading_list[5], P1, R1, F1)

heading_list = ["Pure Llama3.1 Bert_Score Evaluation", "Llama3.1 based Model", "Llama3.1 based Model With hyperparameter tweaking","Pure Llama3.2 Bert_Score Evaluation", "Llama3.2 based Model", "Llama3.2 based Model With hyperparameter tweaking" ]

value_list = ["llama3.1", "llama3.1_without", "llama3.1_with","llama3.2", "llama3.2_without", "llama3.2_with"]

if __name__ == "__main__":
    print_bert_average()
