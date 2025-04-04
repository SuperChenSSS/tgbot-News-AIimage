import requests
import json
import logging
import mysql_db
import datetime
import os

topic_token = "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB"
api_key = "13318211488e6c5d5fc5f20dd1d6fe74bd57962b1ba7425b4cbd243d2a11b453"
url = f"https://serpapi.com/search?engine=google_news&gl=hk&topic_token={topic_token}&api_key={api_key}"

payload = {}
headers = {}

def latest_news(con="", num_max=10):
    current_date = datetime.datetime.today().strftime('%Y-%m-%d-%H')
    news_dir = "news"
    is_dump = True
    if not os.path.exists(news_dir):
        os.makedirs(news_dir)
    response_file = os.path.join(news_dir, f"response-{current_date}.json")
    if os.path.exists(response_file):
        with open(response_file, "r") as f:
            data = json.load(f)
            is_dump = False
            logging.info("Using cached results")
    else:
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        json.dump(data, open(response_file, "w"), indent=4, ensure_ascii=False)
    news_results = data.get("news_results")
    results = {}
    num_data = 0
    for news in news_results:
        #print(news)
        stories = news.get("stories")
        #print(stories)
        if stories:
            for story in stories:
                title = story["title"]
                link = story["link"]
                if title and link and num_data < num_max:
                    num_data += 1
                    results[title] = link
    if is_dump:
        mysql_db.insert_news("news", con, results)
    return results

if __name__ == "__main__":
    results = latest_news()
    # print(results)