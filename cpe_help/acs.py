import pandas
import requests

from cpe_help.util.configuration import get_configuration
from cpe_help.util.misc import grouper


class ACS(object):
    """
    I will help with the retrieval of data from the ACS web API

    Note that only the 5 year estimates will be available through this
    class.
    """
    def __init__(self, year, key):
        """
        Initialize a new ACS object

        Parameters
        ----------
        year : int
            The last year to retrieve data from. For example, if
            year=2015, retrieve data from 2011-2015.
        key : str
            A key used to make requests for the data.
        """
        self.year = year
        self.key = key

    def __repr__(self):
        """
        Represent the ACS object
        """
        return f"ACS(year={self.year!r}, key={self.key!r})"

    def _query(self, variables, geography='us', inside=None):
        """
        Query the ACS API and returns the result as a list of lists

        Parameters
        ----------
        variables : list of str
            A list of variable names to query for.

            The list must not contain more than 50 elements.

            Example:

            ["B01001_002E", "B01001_026E"]
        geography : str, default 'us'
            The unit to retrieve statistics from. For example, if you
            want to retrieve statistics for census tracts, set
            geography='tract'.

            A complete list of geographies can be found here (look at
            the leftmost column):

            https://api.census.gov/data/2016/acs/acs5/examples.html
        inside : str, default None
            Restricts the search inside a specified area. For example,
            if you only want results inside the state of Alabama, you
            can set inside to:

            'state:01'

            If you want to nest deeper, you can specify the needed
            geographies in order. For example:

            'state:01 county:001'

            Will filter the results to Autauga County, Alabama.

        Returns
        -------
        list of lists
            The first list contains the variable names while the others
            carry the requested values.
        """
        # API limit
        assert len(variables) <= 50

        # generate query params
        params = {
            'get': ','.join(variables),
            'for': '{}:*'.format(geography),
        }
        if inside is not None:
            params['in'] = inside
        if self.key != '':
            params['key'] = self.key

        # generate query url
        query_url = f'https://api.census.gov/data/{self.year}/acs/acs5'

        r = requests.get(query_url, params=params)
        r.raise_for_status()

        o = r.json()

        return o

    def data(self, variables, geography='us', inside=None):
        """
        Query the ACS API and return the result as a pandas DataFrame

        Multiple requests will be made if needed.

        Parameters
        ----------
        variables : list of str
            A list of variable names to query for.

            Example:

            ["B01001_002E", "B01001_026E"]
        geography : str, default 'us'
            The unit to retrieve statistics from. For example, if you
            want to retrieve statistics for census tracts, set
            geography='tract'.

            A complete list of geographies can be found here (look at
            the leftmost column):

            https://api.census.gov/data/2016/acs/acs5/examples.html
        inside : str, default None
            Restricts the search inside a specified area. For example,
            if you only want results inside the state of Alabama, you
            can set inside to:

            'state:01'

            If you want to nest deeper, you can specify the needed
            geographies in order. For example:

            'state:01 county:001'

            Will filter the results to Autauga County, Alabama.

        Returns
        -------
        pandas.DataFrame
        """
        dframes = []

        # split variables into chunks of 50
        for chunk in grouper(variables, 50):
            json_result = self._query(chunk, geography, inside)

            # generate DataFrame from chunk result
            columns = json_result[0]
            values = json_result[1:]
            dframe_result = pandas.DataFrame(values, columns=columns)
            dframes.append(dframe_result)

        result = pandas.concat(dframes, axis=1)
        # remove duplicate columns (caused by split requests)
        result = result.loc[:, ~result.columns.duplicated(keep='last')]

        return result


def get_acs():
    """
    Return a default ACS instance (based on configuration)
    """
    config = get_configuration()
    key = config['Census']['Key']
    year = config['Census'].getint('Year')
    return ACS(year, key)
