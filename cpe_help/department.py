"""
This is the main file for dealing with departments

Probably will become the main file of the project.
"""

from importlib import import_module

import geopandas as gpd
import pandas as pd

from cpe_help.acs import get_acs
from cpe_help.census import Census
from cpe_help.util import crs
from cpe_help.util.io import (
    load_json,
    load_zipshp,
    save_json,
    save_zipshp,
)
from cpe_help.util.configuration import get_acs_variables
from cpe_help.util.path import DATA_DIR, maybe_rmfile


class InputError(Exception):
    pass


class Department():
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
    def processed_path(self):
        return self.path / 'processed'

    @property
    def external_acs_path(self):
        return self.external_path / 'ACS'

    @property
    def external_shapefile_path(self):
        return self.external_path / 'police_districts'

    @property
    def preprocessed_shapefile_path(self):
        return self.preprocessed_path / 'police_districts.zip'

    @property
    def guessed_state_path(self):
        return self.path / 'guessed_state.json'

    @property
    def guessed_counties_path(self):
        return self.path / 'guessed_counties.json'

    @property
    def guessed_census_tracts_path(self):
        return self.path / 'guessed_census_tracts.json'

    @property
    def bg_values_path(self):
        return self.raw_path / 'bg_values.pkl'

    @property
    def merged_block_groups_path(self):
        return self.processed_path / 'block_groups.zip'

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

        Note that the source is a usual shapefile, while the destination
        is a shapefile in a zip archive (a single file facilitates
        pipelining).
        """
        raw = self.load_external_shapefile()

        if not raw.crs:
            msg = f"Department {self.name} has no projection defined"
            raise InputError(msg)
        pre = raw.to_crs(crs.epsg4326)

        self.save_preprocessed_shapefile(pre)

    def remove_preprocessed_shapefile(self):
        maybe_rmfile(self.preprocessed_shapefile_path)

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

    def remove_guessed_state(self):
        maybe_rmfile(self.guessed_state_path)

    def guess_counties(self):
        """
        Guess the counties that make part of this department
        """
        census = Census()
        counties = census.load_county_boundaries()
        counties = counties.set_index('COUNTYFP')

        shape = self.load_preprocessed_shapefile()
        shape = shape.to_crs(counties.crs)
        union = shape.unary_union

        intersecting = [ix for ix, geom in counties.geometry.iteritems()
                        if union.intersects(geom)]
        self.save_guessed_counties(intersecting)

    def remove_guessed_counties(self):
        maybe_rmfile(self.guessed_counties_path)

    def guess_census_tracts(self):
        """
        Find relevants census tracts for this department
        """
        census = Census()

        state = self.load_guessed_state()
        police_districts = self.load_preprocessed_shapefile()
        tracts = census.load_tract_boundaries(state)

        police_districts = police_districts.to_crs(tracts.crs)
        unary_union = police_districts.unary_union
        relevant_geoids = [geoid
                           for geoid, geom in zip(
                               tracts['GEOID'],
                               tracts.geometry
                           ) if geom.intersects(unary_union)]

        if len(relevant_geoids) == 0:
            raise RuntimeError(f"Found no intersecting census tracts for Dept."
                               f" {self.name}. Please doule check the"
                               f" Coordinate Reference System.")

        self.save_guessed_census_tracts(relevant_geoids)

    def remove_guessed_census_tracts(self):
        maybe_rmfile(self.guessed_census_tracts_path)

    def download_bg_values(self):
        """
        Download ACS values for relevant block groups

        Relevant block groups are those inside counties that compose
        this department.
        """
        acs = get_acs()
        state = self.load_guessed_state()
        counties = self.load_guessed_counties()
        variables = get_acs_variables()

        # must make 1 request per county
        frames = []
        for county in counties:
            df = acs.data(
                variables,
                geography='block group',
                inside='state:{} county:{}'.format(state, county),
            )
            frames.append(df)
        frame = pd.concat(frames)
        self.save_bg_values(frame)

    def remove_bg_values(self):
        maybe_rmfile(self.bg_values_path)

    def merge_block_groups(self):
        """
        Merge block group values with geography (intersecting counties)
        """
        tiger = TIGER()

        state = self.load_guessed_state()
        counties = self.load_guessed_counties()

        boundaries = tiger.load_bg_boundaries(state)
        boundaries = boundaries[
            (boundaries['STATEFP'] == state) &
            (boundaries['COUNTYFP'].isin(counties))
        ]
        values = self.load_bg_values()
        assert boundaries.shape[0] == values.shape[0]

        index1 = ['STATEFP', 'COUNTYFP', 'TRACTCE', 'BLKGRPCE']
        to_join1 = boundaries.set_index(index1)
        to_join1 = to_join1[['geometry']]

        index2 = ['state', 'county', 'tract', 'block group']
        to_join2 = values.set_index(index2)

        to_join1.index.names = to_join2.index.names
        joined = to_join1.join(to_join2)
        assert joined.shape[0] == boundaries.shape[0]

        # move geometry column to end
        geometry = joined.pop('geometry')
        joined['geometry'] = geometry

        # GeoDataFrame.to_file() ignores indexes
        joined = joined.reset_index()

        self.save_merged_block_groups(joined)

    def remove_merged_block_groups(self):
        maybe_rmfile(self.merged_block_groups_path)

    # input/ouput

    def load_external_shapefile(self):
        path = str(self.external_shapefile_path)
        return gpd.read_file(path)

    def load_preprocessed_shapefile(self):
        return load_zipshp(self.preprocessed_shapefile_path)

    def save_preprocessed_shapefile(self, df):
        save_zipshp(df, self.preprocessed_shapefile_path)

    def load_guessed_state(self):
        return load_json(self.guessed_state_path)

    def save_guessed_state(self, geoid):
        save_json(geoid, self.guessed_state_path)

    def load_guessed_counties(self):
        return load_json(self.guessed_counties_path)

    def save_guessed_counties(self, lst):
        save_json(lst, self.guessed_counties_path)

    def load_guessed_census_tracts(self):
        return load_json(self.guessed_census_tracts_path)

    def save_guessed_census_tracts(self, lst):
        save_json(lst, self.guessed_census_tracts_path)

    def save_bg_values(self, df):
        df.to_pickle(self.bg_values_path)

    def load_bg_values(self):
        return pd.read_pickle(self.bg_values_path)

    def save_merged_block_groups(self, df):
        save_zipshp(df, self.merged_block_groups_path)

    def load_merged_block_groups(self):
        return load_zipshp(self.merged_block_groups_path)


class DepartmentColl():
    """
    Represents a collection of all departments in the data
    """
    @property
    def path(self):
        return DATA_DIR / 'departments'

    @property
    def list_of_departments_path(self):
        return self.path / 'list_of_departments.json'

    @property
    def list_of_states_path(self):
        return self.path / 'list_of_states.json'

    # doit actions

    def create_list_of_departments(self):
        cpe_data = DATA_DIR / 'inputs' / 'cpe-data'
        depts = [Department(d.name[5:])
                 for d in cpe_data.iterdir()
                 if d.is_dir()]
        depts = sorted(depts, key=lambda x: x.name)
        self.save_list_of_departments(depts)

    def remove_list_of_departments(self):
        maybe_rmfile(self.list_of_departments_path)

    def create_list_of_states(self):
        """
        Create a list of states where the departments are

        (to later retrieve census tracts from those)
        """
        states = [dept.load_guessed_state()
                  for dept in self.load_list_of_departments()]
        states = set(states)
        states = sorted(states)
        self.save_list_of_states(states)

    def remove_list_of_states(self):
        """
        Remove the list of states
        """
        maybe_rmfile(self.list_of_states_path)

    # input/output

    def load_list_of_departments(self):
        names = load_json(self.list_of_departments_path)
        depts = [Department(name) for name in names]
        return depts

    def save_list_of_departments(self, lst):
        names = [dept.name for dept in lst]
        save_json(names, self.list_of_departments_path)

    def load_list_of_states(self):
        return load_json(self.list_of_states_path)

    def save_list_of_states(self, lst):
        save_json(lst, self.list_of_states_path)


def list_departments():
    """
    Returns a list with all available Department's

    This is a shortcut.
    """
    dept_coll = DepartmentColl()
    return dept_coll.load_list_of_departments()


def list_states():
    """
    Returns a list with all states where the departments are
    """
    dept_coll = DepartmentColl()
    return dept_coll.load_list_of_states()
