"""
Module for department 37-00027 (Austin, TX)
"""

import collections

import geopandas
import numpy
import pandas
import shapely.geometry

from cpe_help import Department, DepartmentFile, util


class Department3700027(Department):

    CRS = util.crs.esri102739

    @property
    def files(self):
        return collections.OrderedDict([
            ('uof', UOF(self)),
        ])

    def load_external_shapefile(self):
        # set up CRS when loading police boundaries
        df = super().load_external_shapefile()
        df.crs = self.CRS
        return df


class UOF(DepartmentFile):

    def __init__(self, department):
        self.department = department

    @property
    def raw_path(self):
        directory = self.department.tabular_input_dir
        return directory / '37-00027_UOF-P_2014-2016_prepped.csv'

    @property
    def processed_path(self):
        directory = self.department.other_output_dir
        return directory / 'uof.geojson'

    def load_raw(self):
        return pandas.read_csv(
            self.raw_path,
            low_memory=False,
            skiprows=[1],
        )

    def load_processed(self):
        return util.io.load_geojson(self.processed_path)

    def process(self):
        df = self.load_raw()

        # process dates

        df['INCIDENT_DATE'] = pandas.to_datetime(
            df['INCIDENT_DATE'],
            format='%m/%d/%Y',
        )

        # process coordinates

        # x and y coordinates are named the same
        xs = df['Y_COORDINATE'].apply(self._coord_to_int)
        ys = df['Y_COORDINATE.1'].apply(self._coord_to_int)

        coords_present = xs.notnull()
        coords_present &= (xs < 1e7)  # there's one outlier

        Point = shapely.geometry.Point
        points = [Point(x, y) if coded else Point()
                  for x, y, coded in zip(xs, ys, coords_present)]
        crs = self.department.CRS
        result = geopandas.GeoDataFrame(df, geometry=points, crs=crs)
        result = result.to_crs(util.crs.DEFAULT)
        result['LOCATION_GEOCODED'] = coords_present

        self._save_processed(result)

    def _coord_to_int(self, coord):
        return numpy.nan if coord in (numpy.nan, '-') else int(coord)

    def _save_processed(self, df):
        # convert empty points to (0, 0) before saving
        Point = shapely.geometry.Point
        df['geometry'] = df['geometry'].apply(
                lambda x: Point(0, 0) if x.is_empty else x)

        util.io.save_geojson(df, self.processed_path)
