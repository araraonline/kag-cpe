"""
Module for department 49-00033 (Los Angeles, CA)
"""

import collections

import geopandas
import pandas
import shapely

from cpe_help import Department, DepartmentFile, util


class Department4900033(Department):

    @property
    def files(self):
        return collections.OrderedDict([
            ('arrests', Arrests(self)),
        ])


class Arrests(DepartmentFile):

    def __init__(self, department):
        self.department = department

    @property
    def raw_path(self):
        directory = self.department.tabular_input_dir
        path = directory / '49-00033_Arrests_2015.csv'
        return path

    @property
    def processed_path(self):
        directory = self.department.other_output_dir
        path = directory / 'arrests.geojson'
        return path

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

        dates = pandas.to_datetime(
            df['INCIDENT_DATE'],
            format='%m/%d/%y %H:%M',
        )

        df['INCIDENT_DATE'] = dates
        df = df.drop('INCIDENT_TIME', axis=1)

        # process location

        # generate geometries from lat/lon
        Point = shapely.geometry.Point
        lats = df['LOCATION_LATITUDE']
        lons = df['LOCATION_LONGITUDE']
        points = [Point(lon, lat) if lon != 0 else Point()
                  for lat, lon in zip(lats, lons)]

        # generate GeoDataFrame
        crs = self.department.load_external_shapefile().crs
        df = geopandas.GeoDataFrame(df, geometry=points, crs=crs)
        df = df.to_crs(util.crs.DEFAULT)

        self._save_processed(df)

    def _save_processed(self, df):
        df['LOCATION_GEOCODED'] = df['geometry'].apply(
                lambda x: not x.is_empty)

        # convert empty points to (0, 0) before saving
        Point = shapely.geometry.Point
        df['geometry'] = df['geometry'].apply(
                lambda x: Point(0, 0) if x.is_empty else x)

        util.io.save_geojson(df, self.processed_path)
