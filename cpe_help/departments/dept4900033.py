"""
Module for department 49-00033
"""

import geopandas
import pandas
import shapely

from cpe_help import Department, util


class Department4900033(Department):
    """
    Class for department 49-00033

    Specified here is an example of how the preprocessing of specific
    department files will proceed.
    """
    @property
    def external_arrests_path(self):
        return self.external_dir / '49-00033_Arrests_2015.csv'
    
    @property
    def preprocessed_arrests_path(self):
        return self.preprocessed_dir / 'arrests_2015.pkl'

    def load_external_arrests(self):
        return pandas.read_csv(
            self.external_arrests_path,
            low_memory=False,
            skiprows=[1],
        )

    def load_preprocessed_arrests(self):
        return pandas.read_pickle(self.preprocessed_arrests_path)

    def save_preprocessed_arrests(self, df):
        df.to_pickle(self.preprocessed_arrests_path)

    def preprocess_arrests(self):
        """
        Preprocess arrests table
        """
        df = self.load_external_arrests()

        # drop time
        df = df.drop('INCIDENT_TIME', axis=1)

        # process date
        df['INCIDENT_DATE'] = pandas.to_datetime(
            df['INCIDENT_DATE'],
            format='%m/%d/%y %H:%M',
        )

        # flag entries without lat/lon
        df['LOCATION_GEOCODED'] = (
            (df['LOCATION_LATITUDE'] != 0.0) |
            (df['LOCATION_LONGITUDE'] != 0.0)
        )

        # infer CRS from shapefile
        crs = self.load_external_shapefile().crs

        # generate geometries from lat/lon
        Point = shapely.geometry.Point
        lat_lst = df['LOCATION_LATITUDE']
        lon_lst = df['LOCATION_LONGITUDE']
        coded_lst = df['LOCATION_GEOCODED']
        geometry = [Point(lon, lat) if coded else Point()
                    for lat, lon, coded in zip(lat_lst, lon_lst, coded_lst)]

        # generate GeoDataFrame
        df = geopandas.GeoDataFrame(df, geometry=geometry, crs=crs)

        # project into default CRS
        df = df.to_crs(util.crs.DEFAULT)

        self.save_preprocessed_arrests(df)

    def remove_preprocessed_arrests(self):
        util.path.maybe_rmfile(self.preprocessed_arrests_path)
