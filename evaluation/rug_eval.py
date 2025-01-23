from rouge import Rouge

import requests
import json

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

def get_article(article_id: int) -> str:
    try:
        response = requests.post(Database.GET_ARTICLE, json={"article_id": article_id})

        if response.status_code != 201:
            raise Exception("Request Err: Failed to fetch article")

        article = json.loads(response.content)
        if "video" in  article["type"]:
            # print("\n", article['id'])
            return "Err"
        return article["body"]

    except Exception as err:
        # print(str(err))
        return "Err"

def get_article_summaries(article_id: int) -> dict:
    try:
        response = requests.get(Database.GET_ARTICLE_SUMMARY, params={"article_id": article_id})
        if response.status_code != 201:
            raise Exception("Request Err: Failed to fetch article")

        summaries: dict = dict(response.json())
        return summaries["article_summary"]

    except Exception as err:
        # print(str(err))
        return {}

def print_score(heading: str, article: str, article_summary: str) -> None:
    print(f"\n{heading}")
    
    # init rouge evaluation class
    rouge = Rouge()
    score= rouge.get_scores(article, article_summary)
    
    for each_score in score:
        for (key,value) in each_score.items():
            print(f"{key}: [ r : {value["r"]:.4f} ,p : {value["p"]:.4f}, f : {value["f"]:.4f} ]")

def get_average(score: dict[str,dict]):
        for (key, value) in score.items():
            print(f"{key}: [ r : {value["r"]:.4f} ,p : {value["p"]:.4f}, f : {value["f"]:.4f} ]")


def print_average():
    # init all articles along with respective summaries as dict
    articles: list = []
    
    llama31_summary: list = []
    llama31_without_summary: list = []
    llama31_with_summary: list = []

    llama32_summary: list = []
    llama32_without_summary: list = []
    llama32_with_summary: list = []

    for article_id in article_range:
        article = get_article(article_id)
        if article == "Err":
            continue

        summaries = get_article_summaries(article_id)
        if summaries == {}:
            continue

        articles.append(article)

        llama31_summary.append(summaries["llama3.1"])
        llama32_summary.append(summaries["llama3.2"])

        llama31_without_summary.append(summaries["llama3.1_without"])
        llama32_without_summary.append(summaries["llama3.2_without"])

        llama31_with_summary.append(summaries["llama3.1_with"])
        llama32_with_summary.append(summaries["llama3.2_with"])

    # init rouge evaluation
    rouge = Rouge()

    print("\nPure Llama3.1 Rouge Evaluation")
    get_average(rouge.get_scores(hyps=articles, refs=llama31_summary, avg=True))

    print("\nPure Llama3.2 Rouge Evaluation")
    get_average(rouge.get_scores(hyps=articles, refs=llama32_summary, avg=True))

    print("\nLlama3.1 based Model")
    get_average(rouge.get_scores(hyps=articles,refs=llama31_without_summary, avg=True))
    
    print("\nLlama3.2 based Model")
    get_average(rouge.get_scores(hyps=articles,refs=llama32_without_summary, avg=True))

    print("\nLlama3.1 based Model With hyperparameter tweaking")
    get_average(rouge.get_scores(hyps=articles,refs=llama31_with_summary, avg=True))

    print("\nLlama3.2 based Model With hyperparameter tweaking")
    get_average(rouge.get_scores(hyps=articles,refs=llama32_with_summary, avg=True))


heading_list = ["Pure Llama3.1 Rouge Evaluation", "Llama3.1 based Model", "Llama3.1 based Model With hyperparameter tweaking","Pure Llama3.2 Rouge Evaluation", "Llama3.2 based Model", "Llama3.2 based Model With hyperparameter tweaking" ]
value_list = ["llama3.1", "llama3.1_without", "llama3.1_with","llama3.2", "llama3.2_without", "llama3.2_with"]
def main():
    for article_id in article_range:
        article = get_article(article_id)
        article_summaries = get_article_summaries(article_id)

        if article_summaries == {}:
            continue

        if article == "Err":
            continue

        for (heading, summary_id) in zip(heading_list, value_list):
            print_score(heading, article, article_summaries[summary_id])




if __name__ == "__main__":
    # main()
    print_average()
