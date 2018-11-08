"""
Module for dealing with spatial interpolation

More specifically, we are interested in areal interpolation, that is,
the process of moving values from one set of polygons (source) to
another (target).
"""

import geopandas
import pandas

from cpe_help import util


def weighted_areas(source, target, ignore_crs=False):
    """
    Perform weighted areal interpolation from source to target

    This method is also called 'overlay'. It is a simple method of areal
    interpolation that makes the assumption that the variable of
    interest is distributed uniformly over the source polygons.

    Parameters
    ----------
    source : geopandas.GeoDataFrame
        Contains the boundaries and values to interpolate from.
        Non-numeric columns will be ignored.
    target : geopandas.GeoSeries
        Contains the boundaries to interpolate to.
    ignore_crs : bool, default False
        If True, it is assumed that both source and target are in the
        same equal-area projection. If False, the geometries are
        reprojected automatically.

        Leave this option the default unless you know what you are doing.

    Returns
    -------
    geopandas.GeoDataFrame
        The result CRS is always the same as target's.
    """

    # checks
    if not isinstance(source, geopandas.GeoDataFrame):
        raise TypeError("source must be a GeoDataFrame")
    if not isinstance(target, geopandas.GeoSeries):
        raise TypeError("target must be a GeoSeries")
    if source.isnull().any(axis=None):
        raise ValueError("source cannot contain null values")

    # CRS conversion and check
    if not ignore_crs:
        if not source.crs or not target.crs:
            raise ValueError(f"when ignore_crs=False, both source and target"
                             f" must have specified a CRS")
        proj = util.crs.equal_area_from_geodf(source)
        original_crs = target.crs
        source = source.to_crs(proj)
        target = target.to_crs(proj)

    source_values = source.select_dtypes(include='number')
    var_names = source_values.columns
    source_geoms = source.geometry
    target_geoms = target.geometry

    # preprocess source
    target_union = target_geoms.unary_union
    source_geoms = source_geoms[source_geoms.intersects(target_union)]

    # check if source contains target
    # must give some tolerance because of projection distortions
    # (if area is 1km^2, tolerance is 1m^2)
    # you may increase tolarance a bit if it gets problematic
    tol = source_geoms.area.min() * 1e-6
    diff = target_geoms.unary_union - source_geoms.unary_union
    if not diff.area < tol:
        raise ValueError("source shapes must contain target shapes")

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
    result = geopandas.GeoDataFrame(
        target_values,
        geometry=target_geoms,
        crs=target_geoms.crs,
    )

    # output must be in target's CRS
    if not ignore_crs:
        result = result.to_crs(original_crs)

    return result
