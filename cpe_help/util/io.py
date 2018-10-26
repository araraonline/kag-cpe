"""
Module for input/output utils
"""

import json

from cpe_help.util.path import ensure_path


def save_json(obj, filename):
    ensure_path(filename)
    with open(filename, mode='w') as f:
        json.dump(obj, f)


def load_json(filename):
    with open(filename, mode='r') as f:
        return json.load(f)
