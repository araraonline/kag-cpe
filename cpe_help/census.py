"""
This is the module for dealing with the American Community Survey (ACS)

Tasks, directories and loading/saving information will be present here.
"""

import geopandas as gpd

from cpe_help.util.compression import unzip
from cpe_help.util.download import download
from cpe_help.util.path import DATA_DIR


class Census(object):
    """
    Main class for dealing with the ACS
    """

    @property
    def path(self):
        return DATA_DIR / 'census' / f'{self.year}'

    @property
    def state_boundaries_shp_path(self):
        return self.path / 'state_boundaries'

    @property
    def state_boundaries_zip_path(self):
        return self.state_boundaries_shp_path.with_suffix('.zip')

    def __init__(self):
        """
        Initialize a Census object
        """
        self.year = 2016

    def download_state_boundaries(self):
        """
        Download state boundaries for the US
        """
        url = (f'https://www2.census.gov/geo/tiger/TIGER{self.year}/'
               f'STATE/tl_{self.year}_us_state.zip')
        dest = self.state_boundaries_zip_path
        download(url, dest)
        unzip(dest, dest.with_suffix(''))

    def load_state_boundaries(self):
        return gpd.read_file(str(self.state_boundaries_shp_path))
