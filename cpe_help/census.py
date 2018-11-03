"""
This is the module for dealing with the American Community Survey (ACS)

Tasks, directories and loading/saving information will be present here.
"""

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

    @property
    def county_boundaries_path(self):
        return self.path / 'county_boundaries.zip'

    def tract_boundaries_path(self, state):
        return self.path / 'states' / state / 'tract_boundaries.zip'

    def bg_boundaries_path(self, state):
        return self.path / 'states' / state / 'bg_boundaries.zip'

    def __init__(self):
        """
        Initialize a Census object
        """
        self.year = 2016

    # doit actions

    def download_state_boundaries(self):
        """
        Download state boundaries for the US
        """
        url = (f'https://www2.census.gov/geo/tiger/TIGER{self.year}/'
               f'STATE/tl_{self.year}_us_state.zip')
        download(url, self.state_boundaries_path)

    def download_county_boundaries(self):
        """
        Download county boundaries for the US
        """
        url = (f'https://www2.census.gov/geo/tiger/TIGER{self.year}/'
               f'COUNTY/tl_{self.year}_us_county.zip')
        download(url, self.county_boundaries_path)

    def download_tract_boundaries(self, state):
        """
        Download tract boundaries for the given state

        Parameters
        ----------
        state : str
            GEOID for the wanted state.
        """
        url = (f'https://www2.census.gov/geo/tiger/TIGER{self.year}/'
               f'TRACT/tl_{self.year}_{state}_tract.zip')
        download(url, self.tract_boundaries_path(state))

    def download_bg_boundaries(self, state):
        """
        Download block group boundaries for the given state

        Parameters
        ----------
        state : str
            GEOID for the wanted state.
        """
        url = (f'https://www2.census.gov/geo/tiger/TIGER{self.year}/'
               f'BG/tl_{self.year}_{state}_bg.zip')
        download(url, self.bg_boundaries_path(state))

    # input/output

    def load_state_boundaries(self):
        """
        Load state boundaries for the US
        """
        return load_zipshp(self.state_boundaries_path)

    def load_county_boundaries(self):
        """
        Load county boundaries for the US
        """
        return load_zipshp(self.county_boundaries_path)

    def load_tract_boundaries(self, state):
        """
        Load tract boundaries for a given state

        Parameters
        ----------
        state : str
            GEOID representing the state.
        """
        return load_zipshp(self.tract_boundaries_path(state))

    def load_bg_boundaries(self, state):
        """
        Load block group boundaries for a given state

        Parameters
        ----------
        state : str
            GEOID representing the state.
        """
        return load_zipshp(self.bg_boundaries_path(state))
