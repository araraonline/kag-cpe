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
        src = str(self.external_shapefile_path)
        dst = str(self.preprocessed_shapefile_path)

        raw = gpd.read_file(src)
        raw.crs = crs.esri102739

        pre = raw.to_crs(crs.epsg4326)

        ensure_path(dst)
        pre.to_file(dst)
