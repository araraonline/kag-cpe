"""
Module for department 24-00098 (St. Paul, MN)
"""

import collections
import functools

import pandas
import shapely.geometry

from cpe_help import Department, DepartmentFile, util


class Department2400098(Department):

    @property
    def files(self):
        return collections.OrderedDict([
            ('vehicle_stops', VehicleStops(self)),
        ])


class VehicleStops(DepartmentFile):

    def __init__(self, department):
        self.department = department

    @property
    def dependencies(self):
        return [
            self.department.police_precincts_path,
        ]

    @property
    def raw_path(self):
        directory = self.department.tabular_input_dir
        return directory / '24-00098_Vehicle-Stops-data.csv'

    @property
    def processed_path(self):
        directory = self.department.other_output_dir
        return directory / 'vehicle_stops.csv'

    def load_raw(self):
        return pandas.read_csv(
            self.raw_path,
            low_memory=False,
            skiprows=[1],
        )

    def load_processed(self):
        return pandas.read_csv(
            self.processed_path,
            low_memory=False,
        )

    def process(self):
        df = self.load_raw()

        # process date and time

        dates = pandas.to_datetime(
            df['INCIDENT_DATE'],
            format='%m/%d/%y %H:%M',
        )

        df['INCIDENT_DATE'] = dates
        df = df.drop('INCIDENT_DATE_YEAR', axis=1)

        # guess districts - the lat/lon points coincide with the
        # districts centroids

        precincts = self.department.load_police_precincts()
        centroids = precincts.set_index('gridnum').centroid

        @functools.lru_cache(maxsize=1100)
        def guess_district_gridnumber(lat, lon):
            point = shapely.geometry.Point(lon, lat)
            distances = centroids.distance(point)
            return distances.idxmin()

        lats = df['LOCATION_LATITUDE']
        lons = df['LOCATION_LONGITUDE']
        districts = [guess_district_gridnumber(lat, lon)
                     for lat, lon in zip(lats, lons)]

        df['LOCATION_DISTRICT'] = districts
        df = df.drop([
            'LOCATION_LATITUDE',
            'LOCATION_LONGITUDE',
        ], axis=1)

        # save

        self._save_processed(df)

    def _save_processed(self, df):
        # convert Timestamp column to str
        _config = util.configuration.get_configuration()
        _dt_format = _config['Output']['DateAndTimeFormat']
        df['INCIDENT_DATE'] = df['INCIDENT_DATE'].dt.strftime(_dt_format)

        df.to_csv(self.processed_path, index=False)
