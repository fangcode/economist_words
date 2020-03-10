#! /usr/bin/env python
# coding=utf-8

"""
@author:Fang Wang
@date:2019-12-11
@desc:
"""
import logging

from pymongo import MongoClient
from common import config_util

# MongoDB connection info
section_name = "mongodb"
HOST = config_util.load_config_by_key(section_name, "host")
PORT = int(config_util.load_config_by_key(section_name, "port"))
DB_NAME = config_util.load_config_by_key(section_name, "dbname")

# create logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


def get_client():
    client = MongoClient(host=HOST, port=PORT)

    return client


def get_collection(coll_name):
    client = get_client()
    db = client.get_database(DB_NAME)
    coll = db.get_collection(coll_name)

    return coll


def insert_many_documents(coll_name, documents):
    coll = get_collection(coll_name)
    result = coll.insert_many(documents)

    if result:
        logging.info("Succeeded to insert {} documents to collection {}. ".format(len(documents), coll_name))
    else:
        logging.error("Failed to insert documents to collection {}. ".format(coll_name))


def insert_doc(coll_name, doc):
    coll = get_collection(coll_name)
    result = coll.insert(doc)

    if result:
        logging.info("Succeeded to insert a documemt to collection {}. ".format(coll_name))
    else:
        logging.error("Failed to insert documents to collection {}. ".format(coll_name))


def update_article_status(coll_name, article_url):
    coll = get_collection(coll_name)
    coll.update_one(
        {"article_url": article_url},
        {"$set": {"status": 1}}
    )
    logging.info("Succeeded to update status to 1 for article {}".format(article_url))
    return
