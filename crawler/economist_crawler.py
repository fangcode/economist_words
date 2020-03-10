#! /usr/bin/python3
# coding:utf-8

"""
@author:Fang Wang
@date:2020-01-09
@desc:
"""

import sys
import random
import time
import logging

import pandas as pd
import lxml.html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

sys.path.append("../")
from common import config_util
from common import db_mongo

ARTICLE_URL_COLLECTION = "article_urls"
ARTICLE_CONTEXT_COLLECTION = "context"

# create logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s")


class EconomistCrawler:
    def __init__(self):
        self.browser = None
        self.home_url = "https://www.economist.com"
        self.edition_url = "https://www.economist.com/printedition/{}"
        self.article_url_collection = ""

    def create_browser(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=options)

        return

    def close_browser(self):
        self.browser.close()

        return

    def login(self):
        section = "economist"
        email = config_util.load_config_by_key(section, "email")
        passwd = config_util.load_config_by_key(section, "passwd")
        self.create_browser()
        self.browser.get(self.home_url)
        login_in_button = self.browser.find_element_by_xpath(
            "//div[@class='ds-masthead-nav-beta__item ds-masthead-nav-beta__item--log-in']/a")
        login_in_button.click()

        input_email = self.browser.find_element_by_xpath(".//input[@type='email']")
        input_email.send_keys(email)
        input_passwd = self.browser.find_element_by_xpath(".//input[@type='password']")
        input_passwd.send_keys(passwd)

        submit_button = self.browser.find_element_by_xpath(".//button[@id='submit-login']")
        submit_button.click()
        logging.info("Succeeded to login in!")
        time.sleep(5)

        # allow cookies
        allow_button = self.browser.find_element_by_xpath(".//button[@id='_evidon-accept-button']")
        allow_button.click()

        return

    def get_article_links_by_date(self, edition_date):
        self.browser.get(self.edition_url.format(edition_date))
        return parse_article_links(self.browser.page_source, edition_date)

    def get_article_content(self, article_url):
        self.browser.get(self.home_url + article_url)
        return self.browser.page_source


def parse_article_links(content, edition_date):
    root = lxml.html.fromstring(content)
    section_ele_list = root.xpath(
        ".//div[@class='main-content__main-column print-edition__content']/ul[@class='list']/li[@class='list__item']")
    result = list()

    for each_section_ele in section_ele_list:
        section_name = each_section_ele.xpath("div/text()")[0]
        article_ele_list = each_section_ele.xpath("./a")
        for each_article_ele in article_ele_list:
            article_url = each_article_ele.xpath("@href")[0]
            article_name = each_article_ele.xpath("span[contains(@class, 'print-edition__link-title')]/text()")[0]
            article_fly_title = ""
            try:
                article_fly_title = each_article_ele.xpath("span[@class='print-edition__link-flytitle']/text()")[0]
            except:
                pass

            each_article_dict = {
                "date": edition_date,
                "section": section_name,
                "article_url": article_url,
                "article_name": article_name,
                "fly_title": article_fly_title,
                "status": 0
            }
            result.append(each_article_dict)

    return result


def crawl_article_urls():
    edition_list = pd.date_range(start="1/1/2015", end="3/10/2020",
                                 freq='W-SAT').strftime('%Y-%m-%d').tolist()

    ec = EconomistCrawler()
    ec.login()

    for each_edition in edition_list:
        try:
            logging.info("Starting to crawl article urls of edition {}".format(each_edition))
            article_infos = ec.get_article_links_by_date(each_edition)
            db_mongo.insert_many_documents(ARTICLE_URL_COLLECTION, article_infos)
            time.sleep(random.randint(2, 5))
        except Exception as e:
            logging.error("Failed to crawl article url of edition {} due to {}".format(each_edition, str(e)))

    logging.info("Succeeded to crawl all article urls")

    return


def get_article_info():
    col = db_mongo.get_collection(ARTICLE_URL_COLLECTION)
    return col.find_one({"status": 0})


def crawl_context():
    ec = EconomistCrawler()
    ec.login()
    time.sleep(20)

    while True:
        try:
            article_info = get_article_info()
            if not article_info:
                break

            time.sleep(random.randint(5, 10))
            context = ec.get_article_content(article_info.get("article_url"))
            if "View subscription options" not in context:
                article_info["context"] = context
                db_mongo.insert_doc(ARTICLE_CONTEXT_COLLECTION, article_info)
                db_mongo.update_article_status(ARTICLE_URL_COLLECTION, article_info.get("article_url"))
            else:
                logging.warning("Skipped to update status due to auth")
                continue
        except Exception as e:
            logging.error("Failed to crawl context due to {}".format(str(e)))
            continue

    ec.close_browser()


if __name__ == "__main__":
    crawl_context()
