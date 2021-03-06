import time
import datetime
import locale
import json
import re
import random
import os
from collections import Counter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import pandas as pd
import numpy as np

from helper_functions import TIMEOUT, get_datetime_published, get_comments, get_content, get_tags, get_comments_count


MAIN_URL = "https://www.rtvslo.si"


def parse_news_article(driver, url):
    # News article page parsing
    try:
        driver.get(url)

        article_data = dict()

        # URL
        article_data["url"] = url

        # AUTHOR
        article_data["author"] = driver.find_element(By.CLASS_NAME, "article-meta").find_element(By.CLASS_NAME, "author-name").get_attribute("textContent")

        # DATE PUBLISHED
        article_data["datetime_published"] = get_datetime_published(driver)

        # CATEGORY
        article_data["category"] = url.split("/")[3]

        # TITLE
        article_data["title"] = driver.find_element(By.CLASS_NAME, "article-header").find_element(By.TAG_NAME, "h1").get_attribute("textContent")

        # SUBTITLE
        article_data["subtitle"] = driver.find_element(By.CLASS_NAME, "subtitle").get_attribute("textContent")

        # HEADLINE
        article_data["headline"] = driver.find_element(By.CLASS_NAME, "lead").get_attribute("textContent")

        # CONTENT
        article_data["content"] = get_content(driver)

        # TAGS
        article_data["tags"] = get_tags(driver)

        # COMMENTS COUNT
        article_data["total_comments"] = get_comments_count(driver)

        # COMMENTS
        article_data["comments"] = get_comments(driver)
        
        return article_data
    
    except NoSuchElementException:
        return dict()
 

def parse_search_results(driver, articles_URLS, path):
    # Search results page parsing
    page_data = []
    for idx, article_URL in enumerate(articles_URLS):

        # parse news article data
        article_data = parse_news_article(driver, article_URL)

        # append to page data list
        page_data.append(article_data)
        
        # save data every 10 articles
        if idx+1 % 10 == 0:
            with open(os.path.join(path, "data", "intermediate_data_export.json"), "a+", encoding='utf-8') as f:
                json.dump(page_data, f, ensure_ascii=True)
                page_data.clear()
                print("Total exported articles:", idx)
    
    return page_data


def retrieve_urls(driver):

    categories = ["slovenija", "gospodarstvo", "evropska-unija", "znanost-in-tehnologija", "zdravje", "crna-kronika",
                    "okolje", "svet", "svet/evropa", "svet/s-in-j-amerika", "svet/bliznji-vzhod", "svet/afrika", 
                    "svet/azija-z-oceanijo", "sport", "kultura", "zabava-in-slog"]

    # Retrieving all articles and their links
    articles_URLS = set()

    for i in categories:

        archive_URL = MAIN_URL + "/" + i + "/" + "arhiv"
        driver.get(archive_URL)
        time.sleep(TIMEOUT)

        for _ in range(50):
            
            articles = driver.find_elements(By.CLASS_NAME, "article-archive-item")
            for article in articles:
                article_URL = article.find_element(By.TAG_NAME, "a").get_attribute("href")
                first_url_param = article_URL.split("/")[3]
                
                # filter out pages that are not directly rtvslo
                if first_url_param == 'enostavno' or first_url_param == 'mmcdebata' or \
                    first_url_param == 'dostopno' or first_url_param == 'radio-si' or \
                    first_url_param == 'capodistria' or first_url_param == 'mmr':
                    continue
                articles_URLS.add(article_URL)
            
                # save urls every 100 articles
                if len(articles_URLS) % 100 == 0:
                    with open(os.path.join(path, "data", "intermediate_url_export.json"), "w", encoding='utf-8') as f:
                        json.dump(list(articles_URLS), f, ensure_ascii=True)
            
            # number of pagination pages
            next_page = driver.find_elements(By.CLASS_NAME, "page-link")
            next_page = next_page[len(next_page) - 1]
            
            if next_page.get_attribute("textContent") == "50":
                break

            driver.execute_script("arguments[0].click();", next_page)
            time.sleep(TIMEOUT)
    
    return articles_URLS


def search(driver, path):
    # Parsing, data merging and final representation
    articles_URLS = list(retrieve_urls(driver))

    with open(os.path.join(path, "data", "urls.json"), "w", encoding='utf-8') as f:
        json.dump(articles_URLS, f, ensure_ascii=True)

    # with open(os.path.join(path, "data", "urls.json"), "r") as f:
    #     articles_URLS = json.loads(f.read())

    data = parse_search_results(driver, articles_URLS, path)
    
    return data


if __name__=="__main__":

    path = os.path.dirname(os.path.abspath(__file__))

    WEB_DRIVER_LOCATION = os.path.join(path, "chromedriver")

    chrome_options = Options()
    # If you comment the following line, a browser will show ...
    # chrome_options.add_argument("--headless")

    #Adding a specific user agent
    chrome_options.add_argument("user-agent=nlp-2022")

    chrome_webdriver_service = Service(WEB_DRIVER_LOCATION)

    print(f"Retrieving web page URL '{MAIN_URL}'")
    driver = webdriver.Chrome(service=chrome_webdriver_service, options=chrome_options)
    driver.get(MAIN_URL)

    # Timeout needed for Web page to render (read more about it)
    time.sleep(TIMEOUT)

    data = search(driver, path)
    # Save data to UTF-8 encoded JSON
    with open(os.path.join(path, "data", "data.json"), "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=True)

    print("Data exported!")

    driver.close()