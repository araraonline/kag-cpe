from cpe_help.util.path import DATA_DIR


class Census(object):
    """
    Helper class for working with the American Community Survey
    """
    @property
    def dir(self):
        return DATA_DIR / 'census' / str(self.year)

    def __init__(self, year):
        self.year = year

    def tract_boundaries_url(self, state_id):
        return (f'https://www2.census.gov/geo/tiger/TIGER{self.year}'
                f'/TRACT/tl_{self.year}_{state_id}_tract.zip')
