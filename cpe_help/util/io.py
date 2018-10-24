"""
Module for input/output utils
"""

import json


def save_json(obj, filename):
    with open(filename, mode='w') as f:
        json.dump(obj, f)


def load_json(filename):
    with open(filename, mode='r') as f:
        return json.load(f)
