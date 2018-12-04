"""
Module for testing IO functionality
"""

from tempfile import NamedTemporaryFile

import geopandas as gpd
import pandas as pd
from pandas.util.testing import assert_frame_equal
from shapely.geometry import Point

from cpe_help.util import io


def test_save_geojson_with_bool():
    df = gpd.GeoDataFrame(
        [[False, True]],
        columns=['a', 'b'],
        geometry=[Point(0, 0)],
    )
    with NamedTemporaryFile(suffix='.json') as fp:
        # reusing the filename may fail on Windows
        # https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile
        tmp = fp.name
        io.save_geojson(df, tmp)
        result = io.load_geojson(tmp)

    expected = gpd.GeoDataFrame(
        [[0, 1]],
        columns=['a', 'b'],
        geometry=[Point(0, 0)],
    )
    assert_frame_equal(result, expected)


def test_save_geojson_with_datetime():
    df = gpd.GeoDataFrame(
        [[pd.to_datetime('2015')]],
        columns=['a'],
        geometry=[Point(0, 0)],
    )
    with NamedTemporaryFile(suffix='.json') as fp:
        # reusing the filename may fail on Windows
        # https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile
        tmp = fp.name
        io.save_geojson(df, tmp)
        result = io.load_geojson(tmp)

    value = result.iloc[0, 0]
    assert isinstance(value, str)
    assert '2015' in value
