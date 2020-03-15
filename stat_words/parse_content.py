#! /usr/bin/python3
# coding:utf-8

"""
@author:Fang Wang
@date:2020-01-09
@desc:
"""

import sys
import random
import re
import time
import logging
import nltk
import json
import xlsxwriter

from readability import Document
from nltk.book import *
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords

sys.path.append("../")
from common import db_mongo

ARTICLE_URL_COLLECTION = "article_urls"
ARTICLE_CONTEXT_COLLECTION = "context"
LIMIT = 10

# create logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s")


def get_contents():
    offset = 0
    words_stat_dict = dict()
    while True:
        col = db_mongo.get_collection(ARTICLE_CONTEXT_COLLECTION)
        result = col.find().skip(offset).limit(LIMIT)
        i = 1
        for each in result:
            try:
                stat_dict = get_words_from_article(each.get("context"))
            except Exception as e:
                logging.error("Failed to parse words from article {} due to {}".format(each.get("article_url"), str(e)))
                continue
            logging.info("STAT: url={} count={}".format(each.get("article_url"), len(stat_dict)))
            for k, v in stat_dict.items():
                if k in words_stat_dict:
                    words_stat_dict[k] = words_stat_dict[k] + v
                else:
                    words_stat_dict[k] = v
            i += 1
            logging.info("STAT: CURRENT count={}".format(len(words_stat_dict)))
        offset += LIMIT

        if i < LIMIT:
            break

    return cleanup_stat_dict(words_stat_dict)


def get_words_from_article(context):
    doc = Document(context)
    cleaner_context = doc.summary()
    cleaner_context = re.sub(r'<.+?>', ' ', cleaner_context)
    cleaner_context = cleaner_context.lower()

    text_stat = nltk.word_tokenize(cleaner_context)
    freq_dist = FreqDist(text_stat)
    stat_dict = dict()
    for k, v in freq_dist.items():
        stat_dict[k] = v

    return stat_dict


def cleanup_stat_dict(stat_dict):
    deleted_keys = list()
    for k, v in stat_dict.items():
        if k.replace("$", "").isdigit():
            deleted_keys.append(k)
        if k.replace(",", "").isdigit():
            deleted_keys.append(k)
        if k.replace(".", "").isdigit():
            deleted_keys.append(k)
        if k.replace("m", "").isdigit():
            deleted_keys.append(k)
        if k.replace("th", "").isdigit():
            deleted_keys.append(k)
        if k.replace("s", "").isdigit():
            deleted_keys.append(k)
        if len(k) <= 2:
            deleted_keys.append(k)

    for x in deleted_keys:
        stat_dict.pop(x, None)

    return stat_dict


def write_stat_dict(stat_dict):
    f = open("stat_result.txt", "w")
    a1_sorted_keys = sorted(stat_dict, key=stat_dict.get, reverse=True)
    for r in a1_sorted_keys:
        f.write("{}\t{}\n".format(r, stat_dict[r]))

    f.close()
    return


def filter_multiple_words():
    with open("stat.json") as f:
        stat_dict = json.loads(f.read())

    lem = WordNetLemmatizer()
    stem = PorterStemmer()
    i = 0
    a1_sorted_keys = sorted(stat_dict, key=stat_dict.get, reverse=True)

    standard_list = list()
    relative_dict = dict()
    new_list = list()

    # for ke in a1_sorted_keys:
    #     if stat_dict[ke] > 10:
    #         standard_list.append(ke)
    #
    # for r in a1_sorted_keys:
    #     i += 1
    #     if i % 10000 == 0:
    #         print(i)
    #
    #     if stat_dict[r] < 3:
    #         continue
    #
    #     stem_word = stem.stem(r)
    #     lem_word = lem.lemmatize(r, "v")
    #
    #     if stem_word in standard_list and stem_word != r and stat_dict[stem_word] > stat_dict[r]:
    #         relative_dict[r] = stem_word
    #
    #     if lem_word in standard_list and lem_word != r:
    #         relative_dict[r] = lem_word
    #
    # for r, t in relative_dict.items():
    #     print(r, t)

    stop_words = set(stopwords.words("english"))
    new_stat = dict()

    for ew in a1_sorted_keys:
        if ew in stop_words:
            continue

        if ew in relative_dict:
            original_word = relative_dict[ew]
            if original_word not in new_stat:
                new_stat[original_word] = stat_dict[ew]
            else:
                new_stat[original_word] += stat_dict[ew]

        else:
            if ew not in new_stat:
                new_stat[ew] = stat_dict[ew]
            else:
                new_stat[ew] += stat_dict[ew]

    # Workbook is created
    wb = xlsxwriter.Workbook("The Economist Words.xlsx", {"strings_to_urls": False})
    # add_sheet is used to create sheet.
    ws = wb.add_worksheet("The Economist Words")
    # ws.write("A1", "Word")
    # ws.write("B1", "Times")

    index = 1
    f = open("words.text", "w")
    for k, v in new_stat.items():
        if v >= 10:
            ws.write("A{}".format(index), k)
            ws.write("B{}".format(index), v)
            f.write("{}\n".format(k))
            index += 1

    f.close()
    wb.close()


def main():
    stat_dict = get_contents()
    with open("stat.json", "w") as f:
        f.write(json.dumps(stat_dict))

    write_stat_dict(stat_dict)
    return


def load_context_by_url(url):
    col = db_mongo.get_collection(ARTICLE_CONTEXT_COLLECTION)
    result = col.find_one({"article_url": url})
    with open("article.html", "w") as f:
        f.write(result.get("context"))
    print(result)


if __name__ == "__main__":
    # load_context_by_url("/asia/2015/03/05/undigested-history")
    # main()
    filter_multiple_words()