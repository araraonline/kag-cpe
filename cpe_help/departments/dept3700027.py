"""
Example department file.

For this specific case, we will to set the projection when loading the
police geography.
"""

from cpe_help import Department
from cpe_help.util import crs


class Department3700027(Department):
    def load_external_shapefile(self):
        df = super().load_external_shapefile()
        df.crs = crs.esri102739
        return df
