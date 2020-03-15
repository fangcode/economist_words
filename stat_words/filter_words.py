#! /usr/bin/python3
# coding:utf-8

"""
@author:Fang Wang
@date:2020-01-09
@desc:
"""

import subprocess
import json
import logging

import lxml.html


# create logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s")


def get_original_word(each_word):
    p = subprocess.Popen(['./dicttool', '-e', each_word],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    original_word = ""

    try:
        root = lxml.html.fromstring(out)
        entry_ele_list = root.xpath(".//entry[@class='entry']")
        for entry_ele in entry_ele_list:
            original_word = entry_ele.attrib.get("d:title")
            return original_word
    except Exception as e:
        logging.error("Failed to parse original word of {} due to {} ".format(each_word, str(e)))

    return original_word


def restat_word_using_dictionary():
    with open("stat.json") as f:
        stat_dict = json.loads(f.read())

    a1_sorted_keys = sorted(stat_dict, key=stat_dict.get, reverse=True)
    new_stat_data = dict()

    for k in a1_sorted_keys:
        real_original_word = get_original_word(k)
        if not real_original_word:
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
    # print(get_original_word("fresher"))
