"""
This is the main file for dealing with departments

Probably will become the main file of the project.
"""

from importlib import import_module

import geopandas as gpd

from cpe_help.util.path import DATA_DIR
from cpe_help.util.path import ensure_path


class InputError(Exception):
    pass


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

    def __new__(cls, name):
        """
        Create a new department object

        This method makes the Department constructor return a specific
        subclass, based on the name.

        Parameters
        ----------
        name : str
            Represents the department name, e.g. '37-00027' for Austin.

        Returns
        -------
        Department object
        """
        # avoid direct instantiation of subclasses
        assert cls == Department

        name = name.replace('-', '')
        module_name = f"cpe_help.departments.dept{name}"
        class_name = f"Department{name}"

        try:
            # instantiate specific subclass
            mod = import_module(module_name)
            klass = getattr(mod, class_name)
            return super().__new__(klass)
        except ModuleNotFoundError:
            # no specific subclass
            # use generic version Department
            return super().__new__(cls)

    def __init__(self, name):
        """
        Initialize a new department object

        Parameters
        ----------
        name : str
            Represents the department name, e.g. '37-00027' for Austin.
        """
        self.name = name

    def __repr__(self):
        return "{klass}({name!r})".format(
            klass=type(self).__name__,
            name=self.name,
        )

    def preprocess_shapefile(self):
        """
        Preprocess the raw shapefile for this department

        The default implementation (Department) copies from the source
        shapefiles to destination, while setting the CRS to EPSG:4326.

        Source: './external/shapefiles'
        Destination: './preprocessed/shapefiles'
        """
        epsg4326 = {
            'init': 'epsg:4326',
            'no_defs': True
        }

        ensure_path(self.dir / 'preprocessed' / 'shapefiles')
        raw = gpd.read_file(str(self.dir / 'external' / 'shapefiles'))

        if not raw.crs:
            raise InputError(f"Department {self.name} has no projection defined")

        pre = raw.to_crs(epsg4326)
        raw.to_file(str(self.dir / 'preprocessed' / 'shapefiles'))


def list_departments():
    """
    Returns a list with all available Department's
    """
    return [Department(x.name) for x in (DATA_DIR / 'departments').iterdir()]
