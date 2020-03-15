#! /usr/bin/python3
# coding:utf-8

"""
@author:Fang Wang
@date:2020-01-09
@desc:
"""

"""
Look up words in macOS dictionary.
Modified from:
http://macscripter.net/viewtopic.php?id=26675
http://apple.stackexchange.com/questions/90040/look-up-a-word-in-dictionary-app-in-terminal
https://gist.github.com/lambdamusic/bdd56b25a5f547599f7f
"""


import re
import sys

try:
    from DictionaryServices import DCSCopyTextDefinition
except ImportError:
    print("ERROR: Missing lib. $ pip install pyobjc-framework-CoreServices")
    sys.exit()

try:
    from colorama import Fore, Style
except ImportError:
    print("ERROR: Missing lib. $ pip install colorama")


def search(search_word):
    """
    define.py
    Access the default OSX dictionary
    """
    try:
        searchword = search_word
    except IndexError:
        errmsg = 'You did not enter any terms to look up in the Dictionary.'
        print(errmsg)
        sys.exit()
    wordrange = (0, len(searchword))
    dictresult = DCSCopyTextDefinition(None, searchword, wordrange)

    if not dictresult:
        errmsg = "'%result' not found in Dictionary." % (searchword)
    else:
        result = dictresult.encode("utf-8")

        arrow = colorize("\n\n\xe2\x96\xb6 ", "red")
        result = result.replace(b'\xe2\x96\xb6', arrow)

        bullet = colorize(u'\n\u2022', "bold")
        result = result.replace(b'\xe2\x80\xa2', bullet)

        phrases_header = colorize("\n\nPHRASES\n", "bold")
        result = result.replace(b'PHRASES', phrases_header)

        derivatives_header = colorize("\n\nDERIVATIVES\n", "bold")
        result = result.replace(b'DERIVATIVES', derivatives_header)

        origin_header = colorize("\n\nORIGIN\n", "bold")
        result = result.replace(b'ORIGIN', origin_header)

        result = result.decode("utf-8")

        for part in ["noun", "verb", "adverb", "adjective"]:
            result = result.replace(f"{part} ", f"\n{Fore.GREEN + part + Style.RESET_ALL}\n")

        for num in range(1, 10):
            result = result.replace(f" {num} ", f"\n{num} ")

        original_word = parse_original_word(result)

        return original_word, result


def parse_original_word(context):
    if context.startswith("-"):
        context = context[1:]
    noun_start = context.find("noun")
    verb_start = context.find("verb")
    adverb_start = context.find("adverb")
    adjective_start = context.find("adjective")
    if noun_start < 0:
        noun_start += 10000
    if verb_start < 0:
        verb_start += 10000
    if adverb_start < 0:
        adverb_start += 10000
    if adjective_start < 0:
        adjective_start += 10000

    min_start = min(noun_start, verb_start, adverb_start, adjective_start)
    slash_start = context.find("|")
    if slash_start < 0:
        slash_start += 10000
    blank_start = context.find(" ")
    if blank_start < 0:
        blank_start += 10000

    quote_start = context.find("(")
    if quote_start < 0:
        quote_start += 10000

    original_word = context[:min(min_start, slash_start, quote_start,
                                 blank_start)].replace("·", "").replace("1", "").replace("\n", "").replace(" ", "")

    return original_word


def colorize(string, style=None):
    """
    Returns a colored string encoded as a sequence of bytes.
    """
    string = str(string)
    if style == "bold":
        string = Style.BRIGHT + string + Style.RESET_ALL
    elif style == "red":
        string = Fore.RED + string + Style.RESET_ALL
    return bytes(string, encoding="utf-8")


PURPLE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


def search_new(searchword):
    wordrange = (0, len(searchword))
    result = DCSCopyTextDefinition(None, searchword, wordrange)
    original_word = ""
    if not result:
        print('{} not found in Dictionary.'.format(searchword))
        return original_word, None
    else:
        # result = re.sub(r'\|(.+?)\|', PURPLE + r'/\1/' + ENDC, result)
        result = re.sub(r'(?<!\d)(\d)(?!\d)\s', '\n ' + BOLD + r'\1: ' + ENDC, result)
        result = re.sub(r'▶', '\n\n ' + RED + '▶ ' + ENDC, result)
        result = re.sub(r'• ', '\n   ' + GREEN + '• ' + ENDC, result)
        # result = re.sub(r'(‘|“)(.+?)(’|”)', YELLOW + r'“\2”' + ENDC, result)
        result = re.sub(r'PHRASES', '\n\n' + YELLOW + 'PHRASES' + ENDC, result)
        result = re.sub(r'DERIVATIVES', '\n\n' + YELLOW + 'DERIVATIVES' + ENDC, result)
        result = re.sub(r'ORIGIN', '\n\n' + YELLOW + 'ORIGIN' + ENDC, result)
        original_word = parse_original_word(result)
        return original_word, result


if __name__ == '__main__':
    # original_word, explation = search("decorations")
    # print(original_word)
    # print(explation)
    search_word = "banks"
    print(search_new(search_word))
