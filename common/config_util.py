#! /usr/bin/python3
# coding:utf-8

"""
@author:Fang Wang
@date:2020-01-09
@desc:
"""
import configparser


def load_config_by_key(section, config_key):
    config = configparser.RawConfigParser()
    config.read("../default.cfg")

    return config.get(section, config_key)