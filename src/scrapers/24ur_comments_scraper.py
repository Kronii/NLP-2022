import time
import datetime
import json
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re

from concurrent.futures import ThreadPoolExecutor
import threading

writer_lock = threading.Lock()

TIMEOUT = 3

PATH = os.path.dirname(os.path.abspath(__file__))

# Parameters
NUM_WORKERS = 10


def initialize_driver():
    WEB_DRIVER_LOCATION = os.path.join(PATH, "chromedriver")

    chrome_options = Options()
    # If you comment the following line, a browser will show ...
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent=nlp-2022")
    chrome_webdriver_service = Service(WEB_DRIVER_LOCATION)
    driver = webdriver.Chrome(service=chrome_webdriver_service, options=chrome_options)
    driver.implicitly_wait(TIMEOUT)
    return driver


def retrieve_num_comments(article):
    if "title" in article["24ur"].keys():

        url = article["24ur"]["url"]

        # Skip if link leads to video content
        if "video" in url:
            article["24ur"]["total_comments"] = -1
            return article

        driver = initialize_driver()
        driver.get(url)
        time.sleep(TIMEOUT)

        retries = 3
        while True:
            try:
                num_comments = driver.find_element(By.XPATH, "//*[@id='onl-article-comments']/div/div[1]/h3/span").get_attribute("textContent")
                num_comments = int("".join(filter(str.isdigit, num_comments)))
                break
            except NoSuchElementException as e:
                print(f"No such element exception... Retrying ({retries})")
                time.sleep(TIMEOUT * 2)
                if retries <= 0:
                    article["24ur"]["total_comments"] = -1
                    return article
                retries -= 1
        
        article["24ur"]["total_comments"] = num_comments

    return article


def run_threads(articles, workers):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return executor.map(retrieve_num_comments, articles)


if __name__=="__main__":

    with open(os.path.join(PATH, "data", "data.json"), "r") as f:
        data = json.loads(f.read())

    run_threads(data, workers=NUM_WORKERS)

    with open(os.path.join(PATH, "data", "final_data.json"), "w") as f:
        json.dump(data, f, ensure_ascii=True)