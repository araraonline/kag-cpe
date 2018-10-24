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
    def load_external_shapefile(self):
        df = super().load_external_shapefile()
        df.crs = crs.esri102739
        return df
