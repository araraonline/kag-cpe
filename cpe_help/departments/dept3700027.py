"""
Example department file.

For this specific case, we will to set the projection when loading the
police geography.
"""

import geopandas as gpd

from cpe_help import Department
from cpe_help.util.path import ensure_path


class Department3700027(Department):
    def preprocess_shapefile(self):
        epsg4326 = {
            'init': 'epsg:4326',
            'no_defs': True
        }

        esri102739 = {
            'datum': 'NAD83',
            'ellps': 'GRS80',
            'lat_0': 29.66666666666667,
            'lat_1': 30.11666666666667,
            'lat_2': 31.88333333333333,
            'lon_0': -100.3333333333333,
            'no_defs': True,
            'proj': 'lcc',
            'to_meter': 0.3048006096012192,
            'x_0': 700000,
            'y_0': 3000000
        }

        raw = gpd.read_file(str(self.dir / 'external' / 'shapefiles'))
        raw.crs = esri102739

        pre = raw.to_crs(epsg4326)
        ensure_path(self.dir / 'preprocessed' / 'shapefiles')
        pre.to_file(str(self.dir / 'preprocessed' / 'shapefiles'))
