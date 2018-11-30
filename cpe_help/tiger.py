"""
This is the module for dealing with the TIGER files

More pragmatically, use this module for retrieving shapefiles based on
different statistical and political divisions!

Ref:

https://www.census.gov/geo/maps-data/data/tiger.html
"""

from cpe_help.util.configuration import get_configuration
from cpe_help.util.download import download
from cpe_help.util.file import maybe_mkdir
from cpe_help.util.io import load_zipshp
from cpe_help.util.path import DATA_DIR


class TIGER():
    """
    Main class for dealing with the TIGER files
    """

    @property
    def path(self):
        return DATA_DIR / 'tiger' / f'{self.year}'

    @property
    def directories(self):
        return [
            self.path,
            self.path / 'STATE',
            self.path / 'COUNTY',
            self.path / 'TRACT',
            self.path / 'BG',
            self.path / 'PLACE',
        ]

    @property
    def state_boundaries_path(self):
        return self.path / 'STATE' / 'us.zip'

    @property
    def county_boundaries_path(self):
        return self.path / 'COUNTY' / 'us.zip'

    def tract_boundaries_path(self, state):
        return self.path / 'TRACT' / f'{state}.zip'

    def bg_boundaries_path(self, state):
        return self.path / 'BG' / f'{state}.zip'

    def place_boundaries_path(self, state):
        return self.path / 'PLACE' / f'{state}.zip'

    def __init__(self, year):
        """
        Initialize a TIGER object

        Parameters
        ----------
        year : int
            Year to retrieve geographies from.
        """
        self.year = year

    def __repr__(self):
        """
        Represent a TIGER object
        """
        return f'TIGER(year={self.year})'

    # doit actions

    def create_directories(self):
        """
        Create the directories where files will be saved
        """
        for dir in self.directories:
            maybe_mkdir(dir)

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

    def download_place_boundaries(self, state):
        """
        Download place boundaries for the US
        """
        url = (f'https://www2.census.gov/geo/tiger/TIGER{self.year}'
               f'/PLACE/tl_{self.year}_{state}_place.zip')
        download(url, self.place_boundaries_path(state))

    # input/output

    def load_state_boundaries(self):
        """
        Load state boundaries for the US

        Returns
        -------
        geopandas.GeoDataFrame
        """
        return load_zipshp(self.state_boundaries_path)

    def load_county_boundaries(self):
        """
        Load county boundaries for the US

        Returns
        -------
        geopandas.GeoDataFrame
        """
        return load_zipshp(self.county_boundaries_path)

    def load_tract_boundaries(self, state):
        """
        Load tract boundaries for a given state

        Parameters
        ----------
        state : str
            GEOID representing the state.

        Returns
        -------
        geopandas.GeoDataFrame
        """
        return load_zipshp(self.tract_boundaries_path(state))

    def load_bg_boundaries(self, state):
        """
        Load block group boundaries for a given state

        Parameters
        ----------
        state : str
            GEOID representing the state.

        Returns
        -------
        geopandas.GeoDataFrame
        """
        return load_zipshp(self.bg_boundaries_path(state))

    def load_place_boundaries(self, state):
        """
        Load place boundaries for a given state

        Cities are in here.

        Parameters
        ----------
        state : str
            GEOID representing the state.

        Returns
        -------
        geopandas.GeoDataFrame
        """
        return load_zipshp(self.place_boundaries_path(state))


def get_tiger():
    """
    Return a default TIGER instance (based on configuration)
    """
    config = get_configuration()
    year = config['Census'].getint('Year')
    return TIGER(year)
