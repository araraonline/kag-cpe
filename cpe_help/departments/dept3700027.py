"""
Example department file.

For this specific case, we will to set the projection when loading the
police geography.
"""

import geopandas as gpd

from cpe_help import Department
from cpe_help.util import crs
from cpe_help.util.path import ensure_path


class Department3700027(Department):
    def preprocess_shapefile(self):
        raw = gpd.read_file(str(self.dir / 'external' / 'shapefiles'))
        raw.crs = crs.esri102739

        pre = raw.to_crs(crs.epsg4326)

        ensure_path(self.dir / 'preprocessed' / 'shapefiles')
        pre.to_file(str(self.dir / 'preprocessed' / 'shapefiles'))
