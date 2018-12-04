"""
Module for (mainly areal) interpolation tests
"""

import functools

import geopandas as gpd
import numpy as np
import pytest
from pandas.util.testing import assert_frame_equal
from shapely.geometry import Point, Polygon

from cpe_help.util import crs
from cpe_help.util.interpolation import weighted_areas
from cpe_help.util.testing import assert_geoframe_almost_equal


class TestWeightedAreas():
    """
    Tests for weighted areal interpolation (overlay)
    """

    def setup_method(self):
        sq1 = Polygon([(0, 0), (0, 2), (2, 2), (2, 0)])
        sq2 = Polygon([(2, 0), (2, 2), (4, 2), (4, 0)])
        self.source = gpd.GeoDataFrame(geometry=[sq1, sq2])
        self.small_source = gpd.GeoDataFrame(geometry=[sq1])

        sq1 = Polygon([(0, 0), (0, 2), (1, 2), (1, 0)])
        sq2 = Polygon([(1, 0), (1, 2), (3, 2), (3, 0)])
        sq3 = Polygon([(3, 0), (3, 2), (4, 2), (4, 0)])
        self.target = gpd.GeoDataFrame(geometry=[sq1, sq2, sq3])
        self.small_target = gpd.GeoDataFrame(geometry=[sq1, sq2])

        point1 = Point(1, 1)
        self.empty_target = gpd.GeoDataFrame(geometry=[point1])

        self.interpolate = functools.partial(weighted_areas, ignore_crs=True)

    # cases where the interpolation should WORK

    def test_identity(self):
        # source == target

        source = self.source
        target = self.source.geometry
        fn = self.interpolate

        source['values'] = [1.0, 2.0]
        source = source[['values', 'geometry']]

        result = fn(source, target)
        expected = source
        assert_frame_equal(result, expected)

    def test_simple(self):
        # source.union = target.union

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source['values'] = [1, 2]
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.5], [1.5], [1]],
            index=target.index,
            columns=['values'],
            geometry=target,
            crs=target.crs,
        )
        assert_frame_equal(result, expected)

    def test_empty_target(self):
        # target is a Point

        source = self.source
        target = self.empty_target.geometry
        fn = self.interpolate

        source['values'] = [1, 2]
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.]],
            index=target.index,
            columns=['values'],
            geometry=target,
            crs=target.crs,
        )
        assert_frame_equal(result, expected)

    def test_small_target(self):
        # source.union > target.union

        source = self.source
        target = self.small_target.geometry
        fn = self.interpolate

        source['values'] = [1, 2]
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.5], [1.5]],
            index=target.index,
            columns=['values'],
            geometry=target,
            crs=target.crs,
        )
        assert_frame_equal(result, expected)

    def test_different_index(self):
        # source and target indexes are in different orders
        # must realign and preserve target order

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source['values'] = [1, 2]
        target = target.reindex([2, 1, 0])

        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[1], [1.5], [0.5]],
            index=[2, 1, 0],
            columns=['values'],
            geometry=target,
            crs=target.crs,
        )
        assert_frame_equal(result, expected)

    def test_0vars(self):
        # 0 variables in source
        # result must have 0 variables

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            index=target.index,
            geometry=target,
            crs=target.crs,
        )  # empty
        assert_frame_equal(result, expected)

    def test_2vars(self):
        # 2 variables in source
        # result must have 2 variables

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source['values1'] = [1, 2]
        source['values2'] = [0, 1]
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.5, 0], [1.5, 0.5], [1, 0.5]],
            index=target.index,
            columns=['values1', 'values2'],
            geometry=target,
            crs=target.crs,
        )
        assert_frame_equal(result, expected)

    def test_1var_with_str(self):
        # 1 non-numeric variable in source
        # result must have 0 variables

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source['values'] = ['A', 'B']
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            index=target.index,
            geometry=target,
            crs=target.crs,
        )  # empty
        assert_frame_equal(result, expected)

    def test_2vars_with_str(self):
        # 1 non-numeric + 1 non-numeric variable in source
        # result must have 1 numeric variable

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source['values1'] = [1, 2]
        source['values2'] = ['A', 'B']
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.5], [1.5], [1]],
            index=target.index,
            columns=['values1'],
            geometry=target,
            crs=target.crs,
        )
        assert_frame_equal(result, expected)

    # cases where the interpolation should FAIL

    def test_small_source(self):
        # source.union must contain target.union

        source = self.small_source
        target = self.target.geometry
        fn = self.interpolate

        with pytest.raises(ValueError):
            fn(source, target)

    def test_wrong_source_type(self):
        # source type must be GeoDataFrame

        source = self.source.geometry  # GeoSeries
        target = self.target.geometry
        fn = self.interpolate

        with pytest.raises(TypeError):
            fn(source, target)

    def test_wrong_target_type(self):
        # target type must be GeoSeries

        source = self.source
        target = self.target  # GeoDataFrame
        fn = self.interpolate

        with pytest.raises(TypeError):
            fn(source, target)

    def test_null_in_source(self):
        # source cannot have null values

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source['values'] = [1, np.nan]
        with pytest.raises(ValueError):
            fn(source, target)


class TestWeightedAreasNoIgnoreCRS():
    """
    Tests for weighted areal interpolation when ignore_crs=False
    """

    def setup_method(self):

        self.crs1 = crs.EPSG4326
        self.crs2 = crs.from_esri(102739)  # equal area

        sq1 = Polygon([(0, 0), (0, 2), (2, 2), (2, 0)])
        sq2 = Polygon([(2, 0), (2, 2), (4, 2), (4, 0)])
        self.source = gpd.GeoDataFrame(geometry=[sq1, sq2])

        sq1 = Polygon([(0, 0), (0, 2), (1, 2), (1, 0)])
        sq2 = Polygon([(1, 0), (1, 2), (3, 2), (3, 0)])
        sq3 = Polygon([(3, 0), (3, 2), (4, 2), (4, 0)])
        self.target = gpd.GeoDataFrame(geometry=[sq1, sq2, sq3])

        self.interpolate = functools.partial(weighted_areas, ignore_crs=False)

    # cases where interpolation should WORK

    def test_same_crs(self):
        # both source and target share the same CRS

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source.crs = self.crs2
        target.crs = self.crs2

        source['values'] = [1, 2]
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.5], [1.5], [1]],
            index=target.index,
            columns=['values'],
            geometry=target,
            crs=target.crs,
        )
        assert_geoframe_almost_equal(result, expected)

    def test_different_crs(self):
        # source and target have different CRS's
        # result should preserve target's CRS

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source.crs = self.crs2
        target.crs = self.crs2
        target = target.to_crs(self.crs1)

        source['values'] = [1, 2]
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.5], [1.5], [1]],
            index=target.index,
            columns=['values'],
            geometry=target,
            crs=target.crs,
        )
        assert_geoframe_almost_equal(result, expected)

    # cases where interpolation should FAIL

    def test_missing_source_crs(self):
        # both source and target must have a CRS

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        target.crs = self.crs1

        with pytest.raises(ValueError):
            fn(source, target)

    def test_missing_target_crs(self):
        # both source and target must have a CRS

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source.crs = self.crs1

        with pytest.raises(ValueError):
            fn(source, target)

    def test_missing_both_crs(self):
        # both source and target must have a CRS

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        with pytest.raises(ValueError):
            fn(source, target)


class TestWeightedAreasIgnoreCRS():
    """
    Tests for weighted areal interpolation when ignore_crs=True
    """

    def setup_method(self):
        self.crs1 = crs.EPSG4326
        self.crs2 = crs.from_esri(102739)  # equal area

        sq1 = Polygon([(0, 0), (0, 2), (2, 2), (2, 0)])
        sq2 = Polygon([(2, 0), (2, 2), (4, 2), (4, 0)])
        self.source = gpd.GeoDataFrame(geometry=[sq1, sq2])

        sq1 = Polygon([(0, 0), (0, 2), (1, 2), (1, 0)])
        sq2 = Polygon([(1, 0), (1, 2), (3, 2), (3, 0)])
        sq3 = Polygon([(3, 0), (3, 2), (4, 2), (4, 0)])
        self.target = gpd.GeoDataFrame(geometry=[sq1, sq2, sq3])

        self.interpolate = functools.partial(weighted_areas, ignore_crs=True)

    # cases where interpolation should WORK (all below)

    def test_same_crs(self):
        # both source and target share the same CRS

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source.crs = self.crs1
        target.crs = self.crs1

        source['values'] = [1, 2]
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.5], [1.5], [1]],
            index=target.index,
            columns=['values'],
            geometry=target,
            crs=target.crs,
        )
        assert_frame_equal(result, expected)

    def test_different_crs(self):
        # source and target have different CRS's
        # result should preserve target's CRS and ignore CRS's in the
        # calculations

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source.crs = self.crs1
        target.crs = self.crs2

        source['values'] = [1, 2]
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.5], [1.5], [1]],
            index=target.index,
            columns=['values'],
            geometry=target,
            crs=target.crs,
        )
        assert_frame_equal(result, expected)

    def test_missing_source_crs(self):
        # source is missing the CRS
        # should preseve target CRS

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        target.crs = self.crs1

        source['values'] = [1, 2]
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.5], [1.5], [1]],
            index=target.index,
            columns=['values'],
            geometry=target,
            crs=target.crs,
        )
        assert_frame_equal(result, expected)

    def test_missing_target_crs(self):
        # target is missing the CRS
        # result should have no CRS

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source.crs = self.crs1

        source['values'] = [1, 2]
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.5], [1.5], [1]],
            index=target.index,
            columns=['values'],
            geometry=target,
        )
        expected.crs = None
        assert_frame_equal(result, expected)

    def test_missing_both_crs(self):
        # source and target are missing the CRS
        # result should have no CRS

        source = self.source
        target = self.target.geometry
        fn = self.interpolate

        source['values'] = [1, 2]
        result = fn(source, target)
        expected = gpd.GeoDataFrame(
            [[0.5], [1.5], [1]],
            index=target.index,
            columns=['values'],
            geometry=target,
        )
        expected.crs = None
        assert_frame_equal(result, expected)
