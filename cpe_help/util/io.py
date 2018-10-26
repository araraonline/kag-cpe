"""
Module for input/output utils
"""

import json

import geopandas as gpd

from cpe_help.util.path import ensure_path


def save_json(obj, filename):
    ensure_path(filename)
    with open(filename, mode='w') as f:
        json.dump(obj, f)


def load_json(filename):
    with open(filename, mode='r') as f:
        return json.load(f)


def load_zipshp(path):
    """
    Load a zipped shapefile

    This is just the usual shapefile, but, instead of the usual
    directory, we keep the contents in a zipfile, for the ease of
    handling.
    """
    # https://commons.apache.org/proper/commons-vfs/filesystems.html
    # using the URI directly doesn't seem documented in fiona
    uri = f'zip://{path}'
    return gpd.read_file(uri)


def save_zipshp(df, path):
    """
    Save a zipped shapefile
    """
    ensure_path(path)

    vfs = f'zip://{path}'
    df.to_file('/', vfs=vfs)
