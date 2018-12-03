import numpy
import geopandas
import pandas.util.testing


def assert_geoframe_almost_equal(left, right):
    """
    Check if left and right are almost equal

    This is needed because projections may produce tiny errors in the
    geometries that are not captured by the pandas tools.

    Parameters
    ----------
    left : geopandas.GeoDataFrame
    right : geopandas.GeoDataFrame
    """
    assert isinstance(left, geopandas.GeoDataFrame)
    assert isinstance(right, geopandas.GeoDataFrame)

    assert left.shape == right.shape

    geom_left = left.geometry
    geom_right = right.geometry

    # elementwise minima
    tol = numpy.minimum(geom_left.area, geom_right.area) * 1e-6
    sym_diff = geom_left.symmetric_difference(geom_right)
    assert (sym_diff.area < tol).all()

    # pandas already accepts close equality of floats
    pandas.util.testing.assert_frame_equal(
        left.drop('geometry', axis=1),
        right.drop('geometry', axis=1),
    )
