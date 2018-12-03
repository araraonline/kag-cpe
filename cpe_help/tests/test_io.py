"""
Module for testing IO functionality
"""

import tempfile

import geopandas
import pandas
from pandas.util.testing import assert_frame_equal
from shapely.geometry import Point

from cpe_help import util


def test_save_geojson_with_bool():
    df = geopandas.GeoDataFrame(
        [[False, True]],
        columns=['a', 'b'],
        geometry=[Point(0, 0)],
    )
    with tempfile.NamedTemporaryFile(suffix='.json') as fp:
        # reusing the filename may fail on Windows
        # https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile
        tmp = fp.name
        util.io.save_geojson(df, tmp)
        result = util.io.load_geojson(tmp)

    expected = geopandas.GeoDataFrame(
        [[0, 1]],
        columns=['a', 'b'],
        geometry=[Point(0, 0)],
    )
    assert_frame_equal(result, expected)


def test_save_geojson_with_datetime():
    df = geopandas.GeoDataFrame(
        [[pandas.to_datetime('2015')]],
        columns=['a'],
        geometry=[Point(0, 0)],
    )
    with tempfile.NamedTemporaryFile(suffix='.json') as fp:
        # reusing the filename may fail on Windows
        # https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile
        tmp = fp.name
        util.io.save_geojson(df, tmp)
        result = util.io.load_geojson(tmp)

    value = result.iloc[0, 0]
    assert isinstance(value, str)
    assert '2015' in value
