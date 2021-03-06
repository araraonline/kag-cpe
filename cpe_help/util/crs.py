"""
Module for defining Coordinate Reference Systems (CRS)

*Do* import this module. Typing '+init esri:102739' every time is very
prone to errors.
"""

import pyproj


def from_epsg(code):
    """
    Return a CRS mapping from the given EPSG code

    Parameters
    ----------
    code : int or str

    Returns
    -------
    dict
        A dictionary representing a PROJ.4 projection.
    """
    return {
        'init': f'epsg:{code}',
        'no_defs': True,
    }


def from_esri(code):
    """
    Return a CRS mapping from the given ESRI code

    Parameters
    ----------
    code : int or str

    Returns
    -------
    dict
        A dictionary representing a PROJ.4 projection.
    """
    return {
        'init': f'esri:{code}',
        'no_defs': True,
    }


def equal_area_from_geodf(df):
    """
    Return equal-area projection for minimum distortion between bounds

    Ref:

    https://proj4.org/operations/projections/aea.html

    Parameters
    ----------
    df : geopandas.GeoDataFrame

    Returns
    -------
    dict
        A dictionary representing a PROJ.4 projection.
    """
    minx, miny, maxx, maxy = df.total_bounds

    p1 = pyproj.Proj(df.crs)
    p2 = pyproj.Proj(EPSG4269)  # NAD83

    minx, miny = pyproj.transform(p1, p2, minx, miny)
    maxx, maxy = pyproj.transform(p1, p2, maxx, maxy)

    return {
        'proj': 'aea',
        'lat_1': miny,
        'lat_2': maxy,
        'lat_0': (miny + maxy) / 2,
        'lon_0': (minx + maxx) / 2,
        'x_0': 0,
        'y_0': 0,
        'ellps': 'GRS80',
        'datum': 'NAD83',
        'units': 'mi',
        'no_defs': True,
    }


# NAD83
EPSG4269 = from_epsg(4269)


# WGS 84
EPSG4326 = from_epsg(4326)


# Default projection for storing files
#
# EPSG:4269 (NAD83) is a good choice because it is the one used by the
# Census. By storing our files in the same projection as the Census, we
# can skip some reprojections.
DEFAULT = EPSG4269
