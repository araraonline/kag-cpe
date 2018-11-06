"""
Module for dealing with spatial interpolation

More specifically, we are interested in areal interpolation, that is,
the process of moving values from one set of polygons (source) to
another (target).
"""

import geopandas
import pandas


def weighted_areas(source, target):
    """
    Perform weighted areal interpolation from source to target

    This method is also called 'overlay'. It is a simple method of areal
    interpolation that makes the assumption that the variable of
    interest is distributed uniformly over the source polygons.

    For this to work, **both source and target must be in an equal-area
    CRS**. The function will produce bad results otherwise.

    Parameters
    ----------
    source : geopandas.GeoDataFrame
        Contains the boundaries and values to interpolate from.
        Non-numeric columns will be ignored.
    target : geopandas.GeoSeries
        Contains the boundaries to interpolate to.

    Returns
    -------
    geopandas.GeoDataFrame
    """

    # checks
    if not isinstance(source, geopandas.GeoDataFrame):
        raise TypeError("source must be a GeoDataFrame")
    if not isinstance(target, geopandas.GeoSeries):
        raise TypeError("target must be a GeoSeries")
    if source.crs != target.crs:
        raise ValueError("source and target CRS's must be the same")
    if source.isnull().any(axis=None):
        raise ValueError("source cannot contain null values")
    if not source.unary_union.contains(target.unary_union):
        raise ValueError("source shapes must contain target shapes")

    source_values = source.select_dtypes(include='number')
    var_names = source_values.columns
    source_geoms = source.geometry
    target_geoms = target.geometry

    # preprocess (speed)
    target_union = target_geoms.unary_union
    source_geoms = source_geoms[source_geoms.intersects(target_union)]

    # algorithm
    target_values = []
    for t_id, t_geom in target_geoms.iteritems():
        # calculate target value (actually an array of values)
        t_value = pandas.Series(0, index=var_names)
        for s_id, s_geom in source_geoms.iteritems():
            if t_geom.intersects(s_geom):
                intersect = t_geom.intersection(s_geom)
                ratio = intersect.area / s_geom.area
                s_value = source_values.loc[s_id]
                t_value += s_value * ratio

        t_value.name = t_id
        target_values.append(t_value)

    # target_values is already in the same order as target_geoms
    return geopandas.GeoDataFrame(
        target_values,
        geometry=target_geoms,
        crs=target_geoms.crs,
    )
