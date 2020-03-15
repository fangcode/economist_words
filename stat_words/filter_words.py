#! /usr/bin/python3
# coding:utf-8

"""
@author:Fang Wang
@date:2020-01-09
@desc:
"""

import sys
import json
import logging

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

sys.path.append("../")
from stat_words import dictionary


# create logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s")


def parse_original_word(k):
    real_original_word = ""

    stop_words = set(stopwords.words("english"))
    lem = WordNetLemmatizer()
    stem = PorterStemmer()

    if k in stop_words:
        return real_original_word

    if "—" in k:
        return real_original_word

    original_word = ""
    try:
        original_word, explation = dictionary.search_new(k)
    except Exception as e:
        logging.error("Failed to look up word {} due to {}".format(k, str(e)))

    if original_word:
        stem_word = stem.stem(k)
        lem_word = lem.lemmatize(k, pos='v')
        dis = nltk.edit_distance(k, original_word)
        sim = 1 - dis / len(k)
        # print(k, original_word, sim, stem_word, lem_word)
        if sim > 0.4 or original_word == stem_word or original_word == lem_word:
            real_original_word = original_word
        else:
            logging.info("Skipped to set original word for {}. original word : {}".format(k, original_word))

    return real_original_word.replace("[32m", "")


def restat_word_using_dictionary():
    with open("stat.json") as f:
        stat_dict = json.loads(f.read())

    a1_sorted_keys = sorted(stat_dict, key=stat_dict.get, reverse=True)
    new_stat_data = dict()

    for k in a1_sorted_keys:
        real_original_word = parse_original_word(k)
        if not real_original_word:
            continue
        if "," in real_original_word or "/" in real_original_word or "'" in real_original_word or \
                "." in real_original_word:
            continue

        if real_original_word not in new_stat_data:
            new_stat_data[real_original_word] = stat_dict.get(k)
        else:
            new_stat_data[real_original_word] += stat_dict.get(k)

    f = open("stat.txt", "w")
    a2_sorted_keys = sorted(new_stat_data, key=new_stat_data.get, reverse=True)
    for j in a2_sorted_keys:
        f.write("{}\t{}\n".format(j, new_stat_data.get(j)))
    f.close()


if __name__ == "__main__":
    restat_word_using_dictionary()
    # print(parse_original_word("took"))
