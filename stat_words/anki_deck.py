#! /usr/bin/python3
# coding:utf-8

"""
@author:Fang Wang
@date:2020-01-09
@desc:
"""

import genanki


def get_model():
    my_model = genanki.Model(
        1607392319,
        'Simple Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ],
        css="text-align: left;"
    )

    return my_model


def get_deck():
    my_deck = genanki.Deck(
        2059400110,
        "The Economist Words")

    return my_deck


def create_note(my_model, word, explation):
    my_note = genanki.Note(
        model=my_model,
        fields=[word, explation])

    return my_note


def package_deck(my_deck):
    genanki.Package(my_deck).write_to_file('output.apkg')


if __name__ == "__main__":
    pass
