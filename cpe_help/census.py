"""
This is the module for dealing with the American Community Survey (ACS)

Tasks, directories and loading/saving information will be present here.
"""

import geopandas as gpd

from cpe_help.util.download import download
from cpe_help.util.io import load_zipshp
from cpe_help.util.path import DATA_DIR


class Census():
    """
    Main class for dealing with the ACS
    """

    @property
    def path(self):
        return DATA_DIR / 'census' / f'{self.year}'

    @property
    def state_boundaries_path(self):
        return self.path / 'state_boundaries.zip'

    def __init__(self):
        """
        Initialize a Census object
        """
        self.year = 2016

    def download_state_boundaries(self):
        url = (f'https://www2.census.gov/geo/tiger/TIGER{self.year}/'
               f'STATE/tl_{self.year}_us_state.zip')
        download(url, self.state_boundaries_path)

    def remove_state_boundaries(self):
        maybe_rmfile(self.state_boundaries_path)

    def load_state_boundaries(self):
        return load_zipshp(self.state_boundaries_path)
