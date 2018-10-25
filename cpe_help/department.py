"""
This is the main file for dealing with departments

Probably will become the main file of the project.
"""

from importlib import import_module

import geopandas as gpd

from cpe_help import Census
from cpe_help.util import crs
from cpe_help.util.io import load_json, save_json
from cpe_help.util.path import DATA_DIR, ensure_path


class InputError(Exception):
    pass


class Department(object):
    """
    Represents a police department

    All department related functionality will be here.
    """

    @property
    def path(self):
        return DATA_DIR / 'departments' / self.name

    @property
    def external_path(self):
        return self.path / 'external'

    @property
    def raw_path(self):
        return self.path / 'raw'

    @property
    def preprocessed_path(self):
        return self.path / 'preprocessed'

    @property
    def external_acs_path(self):
        return self.external_path / 'ACS'

    @property
    def external_shapefile_path(self):
        return self.external_path / 'police_districts'

    @property
    def preprocessed_shapefile_path(self):
        return self.preprocessed_path / 'police_districts'

    @property
    def guessed_state_path(self):
        return self.path / 'guessed_state.json'

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

    # doit actions

    def preprocess_shapefile(self):
        """
        Preprocess the raw shapefile for this department

        The default implementation (Department) copies from source to
        destination, while setting the Coordinate Reference System to
        EPSG:4326.
        """
        raw = self.load_external_shapefile()

        if not raw.crs:
            raise InputError(f"Department {self.name} has no projection defined")
        pre = raw.to_crs(crs.epsg4326)

        self.save_preprocessed_shapefile(pre)

    def guess_state(self):
        """
        Guess the state this department is in
        """
        census = Census()
        states = census.load_state_boundaries()
        states = states.set_index('GEOID')

        shape = self.load_preprocessed_shapefile()
        shape = shape.to_crs(states.crs)
        union = shape.unary_union

        intersecting = [ix for ix, geom in states.geometry.iteritems()
                        if union.intersects(geom)]
        assert len(intersecting) == 1

        self.save_guessed_state(intersecting[0])

    # input/ouput

    def load_external_shapefile(self):
        path = str(self.external_shapefile_path)
        return gpd.read_file(path)

    def load_preprocessed_shapefile(self):
        path = str(self.preprocessed_shapefile_path)
        return gpd.read_file(path)

    def save_preprocessed_shapefile(self, df):
        path = str(self.preprocessed_shapefile_path)
        ensure_path(path)
        df.to_file(path)

    def save_guessed_state(self, geoid):
        save_json(geoid, self.guessed_state_path)

    def load_guessed_state(self):
        return load_json(self.guessed_state_path)


def list_departments():
    """
    Returns a list with all available Department's
    """
    return [Department(x.name) for x in (DATA_DIR / 'departments').iterdir()]
