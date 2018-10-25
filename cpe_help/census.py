"""
This is the module for dealing with the American Community Survey (ACS)

Tasks, directories and loading/saving information will be present here.
"""

from cpe_help.util.path import DATA_DIR


class Census(object):
    """
    Main class for dealing with the ACS
    """

    @property
    def path(self):
        return DATA_DIR / 'census' / f'{self.year}'

    @property
    def state_boundaries_path(self):
        return self.path / 'state_boundaries.zip'

    def __init__(self, year=2016):
        """
        Initialize a Census object

        Parameters
        ----------
        year : int
            The year of the Census to retrieve information from.
            Multiple years can be used/stored together if you use
            different objects.
        """
        self.year = year

    def download_state_boundaries(self):
        """
        Download state boundaries for the US
        """
        url = (f'https://www2.census.gov/geo/tiger/TIGER{self.year}/'
               f'STATE/tl_{self.year}_us_state.zip')
        dest = self.state_boundaries_path
        return download(url, dest)
