"""
This is the main file for dealing with departments

Probably will become the main file of the project.
"""

from importlib import import_module

import geopandas as gpd

from cpe_help.util import crs
from cpe_help.util.io import save_json
from cpe_help.util.path import DATA_DIR, ensure_path


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

        The default implementation (Department) copies from source to
        destination, while setting the Coordinate Reference System to
        EPSG:4326.

        Source: './external/shapefiles'
        Destination: './preprocessed/shapefiles'
        """
        raw = gpd.read_file(str(self.dir / 'external' / 'shapefiles'))

        if not raw.crs:
            raise InputError(f"Department {self.name} has no projection defined")
        pre = raw.to_crs(crs.epsg4326)

        ensure_path(self.dir / 'preprocessed' / 'shapefiles')
        pre.to_file(str(self.dir / 'preprocessed' / 'shapefiles'))

    def guess_state(self):
        """
        Guess which state this department is in

        To guess the state, we find states that intersect with the
        department shape. If there is exactly one state, we're set.
        """
        states = gpd.read_file(str(DATA_DIR / 'census' / '2016' / 'state_boundaries'))
        states = states.set_index('GEOID')

        districts = gpd.read_file(str(self.dir / 'preprocessed' / 'shapefiles'))
        districts = districts.to_crs(states.crs)
        districts = districts.unary_union

        intersecting = [s
                        for s, g in states.geometry.iteritems()
                        if g.intersects(districts)]
        assert len(intersecting) == 1

        save_json(intersecting[0], self.dir / 'state.json')


def list_departments():
    """
    Returns a list with all available Department's
    """
    return [Department(x.name) for x in (DATA_DIR / 'departments').iterdir()]
