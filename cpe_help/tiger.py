"""
This is the module for dealing with the TIGER files

More pragmatically, use this module for retrieving shapefiles based on
different statistical and political divisions!

Ref:

https://www.census.gov/geo/maps-data/data/tiger.html
"""

from cpe_help import util


class TIGER():
    """
    Main class for dealing with the TIGER files
    """

    @property
    def path(self):
        return util.path.DATA_DIR / 'tiger' / f'{self.year}'

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

    def __init__(self, year=None):
        """
        Initialize a TIGER object

        Parameters
        ----------
        year : None or int
            Year to retrieve geographies from. If None, use the
            year present in the configuration file.
        """
        if year is None:
            config = util.get_configuration()
            year = config['Census'].getint('Year')

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
            util.files.maybe_mkdir(dir)

    def download_state_boundaries(self):
        """
        Download state boundaries for the US
        """
        url = (f'https://www2.census.gov/geo/tiger/TIGER{self.year}/'
               f'STATE/tl_{self.year}_us_state.zip')
        util.network.download(url, self.state_boundaries_path)

    def download_county_boundaries(self):
        """
        Download county boundaries for the US
        """
        url = (f'https://www2.census.gov/geo/tiger/TIGER{self.year}/'
               f'COUNTY/tl_{self.year}_us_county.zip')
        util.network.download(url, self.county_boundaries_path)

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
        util.network.download(url, self.tract_boundaries_path(state))

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
        util.network.download(url, self.bg_boundaries_path(state))

    def download_place_boundaries(self, state):
        """
        Download place boundaries for the US
        """
        url = (f'https://www2.census.gov/geo/tiger/TIGER{self.year}'
               f'/PLACE/tl_{self.year}_{state}_place.zip')
        util.network.download(url, self.place_boundaries_path(state))

    # input/output

    def load_state_boundaries(self):
        """
        Load state boundaries for the US

        Returns
        -------
        geopandas.GeoDataFrame
        """
        return util.io.load_zipshp(self.state_boundaries_path)

    def load_county_boundaries(self):
        """
        Load county boundaries for the US

        Returns
        -------
        geopandas.GeoDataFrame
        """
        return util.io.load_zipshp(self.county_boundaries_path)

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
        return util.io.load_zipshp(self.tract_boundaries_path(state))

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
        return util.io.load_zipshp(self.bg_boundaries_path(state))

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
        return util.io.load_zipshp(self.place_boundaries_path(state))
