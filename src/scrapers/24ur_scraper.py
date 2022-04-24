from reprlib import recursive_repr
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

MAIN_URL = "https://www.24ur.com/"
PATH = os.path.dirname(os.path.abspath(__file__))

# Parameters
START_PAGE = 200
END_PAGE = 10000
NUM_WORKERS = 10


def initialize_driver():
    WEB_DRIVER_LOCATION = os.path.join(PATH, "chromedriver")

    chrome_options = Options()
    # If you comment the following line, a browser will show ...
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent=nlp-2022")
    chrome_webdriver_service = Service(WEB_DRIVER_LOCATION)
    driver = webdriver.Chrome(service=chrome_webdriver_service, options=chrome_options)
    driver.implicitly_wait(TIMEOUT)
    return driver


def to_datetime(date_string):
    publish_meta_list = re.split(', |\.|\:', date_string)

    day = int(publish_meta_list[0])
    month = int(publish_meta_list[1])
    year = int(publish_meta_list[2])

    hour, minute = 0, 0
    if len(publish_meta_list) > 3:
        hour = int(publish_meta_list[3])
        minute = int(publish_meta_list[4])

    return str(datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute))


def retrieve_urls(url):

    driver = initialize_driver()
    driver.get(url)
    time.sleep(TIMEOUT)

    retries = 3
    while True:
        content = driver.find_element(By.XPATH, "/html/body/onl-root/div[1]/div[3]/div[1]/onl-search/div/div/div/main/div/div[3]")
        articles = content.find_elements(By.TAG_NAME, "a")
        dates = driver.find_elements(By.XPATH, "//div[@class='text-16 text-black/60 mb-16']")
    
        if (len(articles) > 0):
            break

        print(f"No such element exception... Retrying ({retries})")
        driver.get(url)
        time.sleep(TIMEOUT * 3)
        if retries <= 0:
            return
        retries -= 1

    articles_data = []
    for idx, article in enumerate(articles):
        articles_data.append(
            {
                "title": article.find_element(By.TAG_NAME, "h2").get_attribute("textContent"),
                "url": article.get_attribute("href"),
                "datetime_published": to_datetime(dates[idx].get_attribute("textContent"))
            }
        )

    with writer_lock:
        with open(os.path.join(PATH, "data", "24ur_url_data.json"), "a+", encoding='utf-8') as f:
            json.dump(articles_data, f, ensure_ascii=True)
            f.write(",")
            print("Exported page:", url)



def run_threads(urls, workers):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return executor.map(retrieve_urls, urls)


if __name__=="__main__":
    review_urls = [
        MAIN_URL + "iskanje?q=&stran=" + str(i) for i in range(START_PAGE, END_PAGE)
    ]

    run_threads(review_urls, workers=NUM_WORKERS)