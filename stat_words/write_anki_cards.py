#! /usr/bin/python3
# coding:utf-8

"""
@author:Fang Wang
@date:2020-01-09
@desc:
"""

import logging
import subprocess

import lxml.html

from stat_words import anki_deck


# create logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s")


def load_words():
    with open("stat.txt") as f:
        text_list = f.readlines()
        words = list()
        for i, each_line in enumerate(text_list):
            word, times = each_line.split("\t")
            word = word.strip()
            times = int(times.strip())
            if times >= 5 and i < 25000:
                words.append(word)

    return words


def get_word_definition_en(each_word, definition_html):
    p = subprocess.Popen(['./dicttool', '-e', each_word],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    root = lxml.html.fromstring(out)

    entry_ele_list = root.xpath(".//entry[@class='entry']")
    for entry_ele in entry_ele_list:
        entry_name = entry_ele.attrib.get("d:title")
        definition_html += "<h5 style='text-align:left'> {} </h5>".format(entry_name)
        for each_ele in entry_ele.getchildren():
            # handle ipa
            if "hg" in each_ele.attrib.get("class"):
                try:
                    ipa_ele = each_ele.xpath(".//span[@class='prx']")[0]
                    ipa_text = "".join(ipa_ele.itertext()).strip()
                    definition_html += "<div class=ipa style='text-align:left'> {} </div>".format(ipa_text)
                except:
                    pass
            # handle definition
            elif "sg" in each_ele.attrib.get("class"):
                sg_ele_list = each_ele.getchildren()
                for each_sg_ele in sg_ele_list:
                    if "se" not in each_sg_ele.attrib.get("class"):
                        continue
                    else:
                        se_ele_list = each_sg_ele.getchildren()
                        for each_se_ele in se_ele_list:
                            if "posg" in each_se_ele.attrib.get("class") or "x_xdh" in each_se_ele.attrib.get("class"):
                                se_name = "".join(each_se_ele.itertext())
                                definition_html += "<h5 style='text-align:left'> {} </h5>".format(se_name)
                            else:
                                se_text = "".join(each_se_ele.itertext())
                                se_text = se_text.replace("•", "<br>  •").strip()
                                definition_html += "<p style='text-align:left'> {} </p>".format(se_text)
            else:
                other_ele_list = each_ele.getchildren()
                other_ele_name = other_ele_list[0].text
                other_ele_text = "".join(each_ele.itertext())
                definition_html += "<h4 style='text-align:left'> {} </h4>".format(other_ele_name)
                definition_html += "<hr />"
                definition_html += "<p style='text-align:left'> {} </p>".format(other_ele_text)

    return definition_html


def get_word_definition_zh(each_word, definition_html):
    p = subprocess.Popen(['./dicttool', '-z', each_word],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    root = lxml.html.fromstring(out)

    try:
        entry_ele_list = root.xpath(".//entry[@class='entry']")
        definition_html += "<h3 style='text-align:left'> Chinese</h3> <hr />"
        for entry_ele in entry_ele_list:
            entry_name = entry_ele.attrib.get("d:title")
            definition_html += "<h5 style='text-align:left'> {} </h5>".format(entry_name)
            for each_ele in entry_ele.getchildren():
                # handle chinese definition
                if "gramb" in each_ele.attrib.get("class"):
                    sg_ele_list = each_ele.getchildren()
                    for each_sg_ele in sg_ele_list:
                        if "posg" in each_sg_ele.attrib.get("class") or "x_xdh" in each_sg_ele.attrib.get("class"):
                            sg_name = "".join(each_sg_ele.itertext())
                            definition_html += "<h5 style='text-align:left'> {} </h5>".format(sg_name)
                        else:
                            se_ele_list = each_sg_ele.getchildren()
                            for each_se_ele in se_ele_list:
                                se_text = "".join(each_se_ele.itertext())
                                se_text = se_text.replace("•", "<br>  •").strip()
                                definition_html += "<p style='text-align:left'> {} </p>".format(se_text)
    except Exception as e:
        logging.warning("Skipped to fill chinese context due to {} ".format(str(e)))

    return definition_html


def build_card_html(word):
    definition_html = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">"""

    definition_html = get_word_definition_en(word, definition_html)

    definition_html = get_word_definition_zh(word, definition_html)
    definition_html += "</body></html>"

    return definition_html


my_deck = anki_deck.get_deck()
my_model = anki_deck.get_model()


def main():
    words = load_words()

    for i, each_word in enumerate(words):
        try:
            definition = build_card_html(each_word)
            if definition:
                my_note = anki_deck.create_note(my_model, each_word, definition)
                my_deck.add_note(my_note)
                logging.info("Succeeded to write anki for word {} .  {}/{}".format(each_word, i+1, len(words)))
            else:
                logging.warning("Skipped to write anki card due to definition not found. [{}]".format(each_word))
                continue
        except Exception as e:
            logging.error("Failed to create note for {} due to {}".format(each_word, str(e)))

    anki_deck.package_deck(my_deck)


if __name__ == "__main__":
    main()
    # load_words()
    # search_word = "tote"
    # build_card_html(search_word)
    # anki_deck.package_deck(my_deck)
    # get_word_definition_zh(search_word)
