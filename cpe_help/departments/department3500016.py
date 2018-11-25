"""
Module for department 35-00016 (Orlando, FL)
"""

import geopandas

from cpe_help import Department


class Department3500016(Department):
    def load_external_shapefile(self):
        """
        Load shapefile for Police Districts
        """
        path = str(self.spatial_input_dir)
        layer = 'OrlandoPoliceDistricts'
        df = geopandas.read_file(path, layer=layer)
        return df
