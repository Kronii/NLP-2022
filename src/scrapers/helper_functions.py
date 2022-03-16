import datetime
import locale
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

TIMEOUT = 2
TIMEOUT_COMMENTS = 1

def get_datetime_published(driver):
    publish_meta = driver.find_element(By.CLASS_NAME, "publish-meta").text
    publish_meta_list = publish_meta.split()

    # setting locale to slovenian
    locale.setlocale(locale.LC_TIME, "sl_SI")

    day = int(publish_meta_list[0][:-1])
    month = int(datetime.datetime.strptime(publish_meta_list[1], "%B").month)
    year = int(publish_meta_list[2])
    time = publish_meta_list[4].split(":")
    hour = int(time[0])
    minute = int(time[1])

    return str(datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute))


def get_content(driver):
    content = ""
    paragraphs = driver.find_element(By.TAG_NAME, "article").find_elements(By.TAG_NAME, "p")
    for p in paragraphs:
        content = content + p.text + " "
    return content


def get_tags(driver):
    return [tag.text for tag in driver.find_element(By.CLASS_NAME, "article-tags").find_elements(By.TAG_NAME, "a")]


def get_comments_count(driver):
    # search for comments count
    total_comments = driver.find_element(By.CLASS_NAME, "numComments").get_attribute("textContent")[1:-1]
    return int(total_comments)


def get_comments(driver):

    # COMMENTS
    comments_btn = driver.find_element(By.CLASS_NAME, "link-show-comments")
    driver.execute_script("arguments[0].click();", comments_btn)
    time.sleep(TIMEOUT_COMMENTS)

    comments_list = []

    # search for comments in the page
    comments = driver.find_elements(By.CLASS_NAME, "comment")
    for comment in comments:
        # retrieve number of elements in comment, since are two if comment is a reply to another comment
        num_elements = len(comment.find_elements(By.CLASS_NAME, "profile-name"))

        if num_elements == 0:
            continue

        # comment properties
        comment_user = comment.find_elements(By.CLASS_NAME, "profile-name")[num_elements - 1].get_attribute(
            "textContent")
        comment_datetime = comment.find_elements(By.CLASS_NAME, "publish-meta")[num_elements].text
        comment_content = comment.find_elements(By.TAG_NAME, "p")[num_elements - 1].get_attribute(
            "textContent").replace('\n', ' ')
        comment_likes = comment.find_elements(By.CLASS_NAME, "comment-vote")[num_elements - 1].get_attribute(
            "textContent")

        comment_dict = dict()
        comment_dict["user"] = comment_user
        comment_dict["date"] = parse_comment_date(comment_datetime)
        comment_dict["comment"] = comment_content
        comment_dict["likes"] = comment_likes

        comments_list.append(comment_dict)

    return comments_list


# HELPER FUNCTIONS
def parse_comment_date(date_string):
    date_string_list = date_string.split()

    if len(date_string_list) != 4:
        return ""
    
    time_list = date_string_list[3].split(":")

    day = int(date_string_list[0][:-1])
    month = int(date_string_list[1][:-1])
    year = int(date_string_list[2][:-1])
    hour = int(time_list[0])
    minute = int(time_list[1])

    return str(datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute))