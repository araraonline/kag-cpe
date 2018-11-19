"""
Module for input/output utils
"""

import json
import pathlib
import tempfile

import geopandas

from cpe_help.util.compression import make_zipfile
from cpe_help.util.files import maybe_rmfile


def save_json(obj, filename):
    with open(filename, mode='w') as f:
        json.dump(obj, f)


def load_json(filename):
    with open(filename, mode='r') as f:
        return json.load(f)


def load_shp(path):
    """
    Load a shapefile

    Parameters
    ----------
    path : str or pathlib.Path

    Returns
    -------
    geopandas.GeoDataFrame
    """
    return geopandas.read_file(str(path))


def save_shp(df, path):
    """
    Save a shapefile

    Parameters
    ----------
    df : geopandas.GeoDataFrame
    path : str or pathlib.Path

    Returns
    -------
    None
    """
    df.to_file(str(path))


def load_geojson(path):
    """
    Load a GeoJSON file

    Parameters
    ----------
    path : str or pathlib.Path

    Returns
    -------
    geopandas.GeoDataFrame
    """
    return geopandas.read_file(str(path), driver='GeoJSON')


def save_geojson(df, path):
    """
    Save a GeoJSON file

    If path already exists, it will be overwritten.

    Parameters
    ----------
    df : geopandas.GeoDataFrame
    path : str or pathlib.Path

    Returns
    -------
    None
    """
    maybe_rmfile(path)
    # XXX: if line below fails, the file will still be removed
    df.to_file(str(path), driver='GeoJSON')


def load_zipshp(path):
    """
    Load a zipped shapefile

    This is just the usual shapefile, but, instead of the usual
    directory, we keep the contents in a zipfile, for the ease of
    handling.
    """
    # https://commons.apache.org/proper/commons-vfs/filesystems.html
    # using the URI directly doesn't seem documented in fiona, but it works
    uri = f'zip://{path}'
    return geopandas.read_file(uri)


def save_zipshp(df, path):
    """
    Save a zipped shapefile
    """
    path = pathlib.Path(path)
    name = path.name

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpname = (pathlib.Path(tmpdir) / name).with_suffix('.shp')
        df.to_file(str(tmpname))
        make_zipfile(path, tmpdir)
