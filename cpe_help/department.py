
"""
This is the main file for dealing with departments

Probably will become the main file of the project.
"""

from cpe_help.util.path import DATA_DIR


class Department(object):
    """
    Represents a police department

    All department related functionality will be here.
    """

    @property
    def dir(self):
        """
        Return the directory containing the department data

        Returns
        -------
        Path
            A pathlib.Path object representing the directory.
        """
        return DATA_DIR / 'departments' / self.name


    def __init__(self, name):
        """
        Initialize a new department object

        Parameters
        ----------
        name : str
            Represents the department name, e.g. '37-00027' for Austin.
        """
        self.name = name


def list_departments():
    """
    Returns a list with all available Department's
    """
    return [Department(x.name) for x in (DATA_DIR / 'departments').iterdir()]
