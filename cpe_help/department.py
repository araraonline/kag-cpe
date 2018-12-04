"""
This is the main file for dealing with departments

Probably will become the main file of the project.
"""

import abc
import collections
import importlib

import fiona
import jinja2
import matplotlib.lines
import matplotlib.patches
import matplotlib.pyplot
import pandas
import us

from cpe_help import util
from cpe_help.acs import ACS
from cpe_help.tiger import TIGER


class InputError(Exception):
    pass


class Department():
    """
    Represents a police department

    All department related functionality will be here.
    """

    @property
    def path(self):
        return util.path.DATA_DIR / 'department' / self.name

    @property
    def input_dir(self):
        return util.path.INPUT_DIR / 'department' / self.name

    @property
    def tabular_input_dir(self):
        return self.input_dir / 'tabular'

    @property
    def spatial_input_dir(self):
        return self.input_dir / 'spatial'

    @property
    def output_dir(self):
        return util.path.OUTPUT_DIR / 'department' / self.name

    @property
    def acs_output_dir(self):
        return self.output_dir / 'acs'

    @property
    def other_output_dir(self):
        return self.output_dir / 'other'

    @property
    def directories(self):
        return [
            self.path,
            self.raw_dir,
            self.preprocessed_dir,
            self.processed_dir,
            self.input_dir,
            self.tabular_input_dir,
            self.spatial_input_dir,
            self.output_dir,
            self.acs_output_dir,
            self.other_output_dir,
            self.sanity_check_dir,
            self.sc_figures_dir,
        ]

    @property
    def raw_dir(self):
        return self.path / 'raw'

    @property
    def preprocessed_dir(self):
        return self.path / 'preprocessed'

    @property
    def processed_dir(self):
        return self.path / 'processed'

    @property
    def preprocessed_shapefile_path(self):
        return self.preprocessed_dir / 'shapefile.zip'

    @property
    def guessed_state_path(self):
        return self.path / 'guessed_state.json'

    @property
    def guessed_counties_path(self):
        return self.path / 'guessed_counties.json'

    @property
    def guessed_city_path(self):
        return self.path / 'guessed_city.json'

    @property
    def tract_values_path(self):
        return self.raw_dir / 'tract_values.pkl'

    @property
    def bg_values_path(self):
        return self.raw_dir / 'bg_values.pkl'

    @property
    def city_stats_path(self):
        return self.processed_dir / 'city_stats.json'

    @property
    def city_path(self):
        return self.processed_dir / 'city.geojson'

    @property
    def census_tracts_path(self):
        return self.processed_dir / 'census_tracts.geojson'

    @property
    def block_groups_path(self):
        return self.processed_dir / 'block_groups.geojson'

    @property
    def police_precincts_path(self):
        return self.processed_dir / 'police_precincts.geojson'

    @property
    def sanity_check_dir(self):
        return self.output_dir / '_sanity_check'

    @property
    def sc_markdown_path(self):
        return self.sanity_check_dir / 'report.md'

    @property
    def sc_html_path(self):
        return self.output_dir / 'sanity_check.html'

    @property
    def sc_figures_dir(self):
        return self.sanity_check_dir / 'figures'

    @property
    def sc_figure1_path(self):
        return self.sc_figures_dir / 'figure1.png'

    @property
    def sc_figure2_path(self):
        return self.sc_figures_dir / 'figure2.png'

    @property
    def sc_figure3_path(self):
        return self.sc_figures_dir / 'figure3.png'

    @property
    def sc_figure4_path(self):
        return self.sc_figures_dir / 'figure4.png'

    @property
    def sc_figure5_path(self):
        return self.sc_figures_dir / 'figure5.png'

    # ACS outputs

    @property
    def city_stats_output(self):
        return self.acs_output_dir / 'city_stats.json'

    @property
    def census_tracts_output(self):
        return self.acs_output_dir / 'census_tracts.geojson'

    @property
    def block_groups_output(self):
        return self.acs_output_dir / 'block_groups.geojson'

    @property
    def police_precincts_output(self):
        return self.acs_output_dir / 'police_precincts.geojson'

    # department-specific files

    @property
    def files(self):
        return collections.OrderedDict([])

    # base

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
        module_name = f"cpe_help.departments.department{name}"
        class_name = f"Department{name}"

        try:
            # instantiate specific subclass
            mod = importlib.import_module(module_name)
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

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{klass}({name!r})".format(
            klass=type(self).__name__,
            name=self.name,
        )

    # utils

    @property
    def city(self):
        """
        Return a string representing my city's name

        Examples
        --------
        >>> dept = Department('11-00091')
        >>> dept.city
        'Boston'
        """
        return self.load_guessed_city()

    def load_city_metadata(self):
        """
        Load data associated with my city from TIGER

        Returns
        -------
        geopandas.GeoDataFrame
            A 1-lined GeoDataFrame whose only entry corresponds to the
            requested data.
        """
        tiger = TIGER()
        places = tiger.load_place_boundaries(self.state.fips)
        places = places[places['NAME'] == self.city]
        assert places.shape[0] == 1
        return places

    @property
    def state(self):
        """
        Return a us.states.State object representing my state

        Reference:

        https://github.com/unitedstates/python-us

        Examples
        --------
        >>> dept = Department('11-00091')
        >>> dept.state
        <State:Massachusetts>
        """
        fips = self.load_guessed_state()
        return us.states.lookup(fips)

    @property
    def location(self):
        """
        Return a string representing my location

        Examples
        --------
        >>> dept = Department('11-00091')
        >>> dept.location
        'Boston, MA'
        """
        return '{}, {}'.format(
            self.city,
            self.state.abbr,
        )

    @property
    def full_name(self):
        """
        Return a string representing my name and location

        Examples
        --------
        >>> dept = Department('11-00091')
        >>> dept.full_name
        '11-00091 (Boston, MA)'
        """
        return '{} ({})'.format(
            self.name,
            self.location,
        )

    @classmethod
    def sample(cls):
        """
        Return one sample department from the list
        """
        return Department.list()[0]

    @classmethod
    def list(cls):
        """
        Return a list with all available Departments
        """
        return DepartmentCollection().list()

    # doit actions

    def create_directories(self):
        """
        Create the directories where files will be saved
        """
        for dir in self.directories:
            util.file.maybe_mkdir(dir)

    def preprocess_shapefile(self):
        """
        Preprocess the raw shapefile for this department

        The default implementation (Department) copies from source to
        destination, while setting the Coordinate Reference System to
        the default (defined at util.crs.DEFAULT).

        Note that the source is a usual shapefile, while the destination
        is a shapefile in a zip archive (a single file facilitates
        pipelining).
        """
        raw = self.load_external_shapefile()

        if not raw.crs:
            msg = f"Department {self.name} has no projection defined"
            raise InputError(msg)
        pre = raw.to_crs(util.crs.DEFAULT)

        self.save_preprocessed_shapefile(pre)

    def guess_state(self):
        """
        Guess the state this department is in
        """
        states = TIGER().load_state_boundaries()
        precincts = self.load_preprocessed_shapefile()

        # set up equal area projection
        proj = util.crs.equal_area_from_geodf(precincts)
        states = states.to_crs(proj)
        precincts = precincts.to_crs(proj)

        # determine state with biggest intersection
        states = states.set_index('GEOID')
        intersection = states.intersection(precincts.unary_union).area
        state = intersection.idxmax()

        self.save_guessed_state(state)

    def guess_counties(self):
        """
        Guess the counties that make part of this city and department
        """
        city = self.load_city_metadata()
        counties = TIGER().load_county_boundaries()
        precincts = self.load_preprocessed_shapefile()

        # speed things up
        city = city.to_crs(counties.crs)
        precincts = precincts.to_crs(counties.crs)

        shape1 = city.geometry.iloc[0]
        shape2 = precincts.unary_union
        union = shape1.union(shape2)

        counties = counties[counties.intersects(union)]

        # set up equal area projection
        proj = util.crs.equal_area_from_geodf(city)
        city = city.to_crs(proj)
        counties = counties.to_crs(proj)
        precincts = precincts.to_crs(proj)

        # calculate union of city and precincts
        shape1 = city.geometry.iloc[0]
        shape2 = precincts.unary_union
        union = shape1.union(shape2)

        # determine counties with plausible intersection
        tol = precincts.area.min() * 1e-6
        counties = counties.set_index('COUNTYFP')
        intersection = counties.intersection(union).area
        intersecting = intersection[intersection > tol].index.tolist()

        self.save_guessed_counties(intersecting)

    def guess_city(self):
        """
        Guess the city this department is in
        """
        tiger = TIGER()

        places = tiger.load_place_boundaries(self.state.fips)
        police = self.load_preprocessed_shapefile()
        police = police.to_crs(places.crs)

        # we want to avoid statistical entities
        # ref: https://www.census.gov/geo/reference/funcstat.html
        # the 'F' is left here for Indianopolis
        # ref: https://en.wikipedia.org/wiki/Indianapolis#Demographics
        places = places[places['FUNCSTAT'].isin(['A', 'F'])]

        # speeding things up
        places = places[places.intersects(police.unary_union)]

        proj = util.crs.equal_area_from_geodf(places)
        places = places.to_crs(proj)
        police = police.to_crs(proj)

        idx = places.intersection(police.unary_union).area.idxmax()
        city_name = places.loc[idx, 'NAME']

        self.save_guessed_city(city_name)

    def download_tract_values(self):
        """
        Download ACS values for relevant census tracts

        Relevant census tracts are those inside counties that compose
        this department.
        """
        acs = ACS()
        state = self.load_guessed_state()
        counties = self.load_guessed_counties()
        variables = util.configuration.get_acs_variables()

        # must make 1 request per county
        frames = []
        for county in counties:
            df = acs.data(
                variables,
                geography='tract',
                inside='state:{} county:{}'.format(state, county),
            )
            frames.append(df)
        frame = pandas.concat(frames)
        self.save_tract_values(frame)

    def download_bg_values(self):
        """
        Download ACS values for relevant block groups

        Relevant block groups are those inside counties that compose
        this department.
        """
        acs = ACS()
        state = self.load_guessed_state()
        counties = self.load_guessed_counties()
        variables = util.configuration.get_acs_variables()

        # must make 1 request per county
        frames = []
        for county in counties:
            df = acs.data(
                variables,
                geography='block group',
                inside='state:{} county:{}'.format(state, county),
            )
            frames.append(df)
        frame = pandas.concat(frames)
        self.save_bg_values(frame)

    def process_city(self):
        """
        Generate statistics for my city

        See also
        --------
        Department.process_police_precincts
        """
        city = self.load_city_metadata()
        bgs = self.load_block_groups()
        new_city = util.interpolation.weighted_areas(bgs, city.geometry)
        joined = city.join(new_city.drop('geometry', axis=1))
        self.save_city(joined)

    def process_census_tracts(self):
        """
        Merge census tract values with geography (for intersecting
        counties)
        """
        tiger = TIGER()

        state = self.load_guessed_state()
        counties = self.load_guessed_counties()

        boundaries = tiger.load_tract_boundaries(state)
        boundaries = boundaries[
            (boundaries['STATEFP'] == state) &
            (boundaries['COUNTYFP'].isin(counties))
        ]
        values = self.load_tract_values()
        assert boundaries.shape[0] == values.shape[0]

        index1 = ['STATEFP', 'COUNTYFP', 'TRACTCE']
        to_join1 = boundaries.set_index(index1)
        to_join1 = to_join1[['geometry']]

        index2 = ['state', 'county', 'tract']
        to_join2 = values.set_index(index2)

        to_join1.index.names = to_join2.index.names
        joined = to_join1.join(to_join2)
        assert joined.shape[0] == to_join1.shape[0]

        # move geometry column to end
        geometry = joined.pop('geometry')
        joined['geometry'] = geometry

        # GeoDataFrame.to_file() ignores indexes
        joined = joined.reset_index()

        self.save_census_tracts(joined)

    def process_block_groups(self):
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

        self.save_block_groups(joined)

    def process_police_precincts(self):
        """
        Generate police precincts file

        This currently made as a join between the externally provided
        shapefiles (proprocessed_shapefile) data and data that comes
        from the Census interpolated into the relevant regions.
        """
        police = self.load_preprocessed_shapefile()
        bgs = self.load_block_groups()
        new_police = util.interpolation.weighted_areas(bgs, police.geometry)
        joined = police.join(new_police.drop('geometry', axis=1))
        self.save_police_precincts(joined)

    def generate_city_stats(self):
        """
        Generate statistics for my city

        The statistics are extracted from the BGs that intersect with
        the city, in a method called areal interpolation.
        """
        city = self.load_city_metadata()
        bgs = self.load_block_groups()
        stats = util.interpolation.weighted_areas(bgs, city.geometry)
        # use stats as a Series without geometry
        stats = stats.iloc[0].drop('geometry')
        self.save_city_stats(stats)

    def generate_sc_markdown(self):
        """
        Generate sanity check report in markdown
        """

        # base
        name = self.name
        klass = type(self).__name__
        inferred_city = self.city
        inferred_state = self.state.name
        base_dir = util.path.DATA_DIR

        # files
        input_files = [f.relative_to(base_dir)
                       for f in util.file.list_files(self.input_dir)]
        output_files = [f.relative_to(base_dir)
                        for f in util.file.list_files(self.output_dir)]

        # input shapefile
        shp_df = util.io.load_shp(self.spatial_input_dir)
        shp_layers = fiona.listlayers(str(self.spatial_input_dir))
        shp_crs = shp_df.crs
        shp_attributes = sorted(set(shp_df.columns) - {'geometry'})

        # load template
        template_path = util.path.TEMPLATES_DIR / 'sanity_check.md'
        with open(template_path, mode='r') as f:
            source = f.read()
            template = jinja2.Template(source)

        # generate text
        result = template.render(
            dept=self,
            name=name,
            klass=klass,
            inferred_city=inferred_city,
            inferred_state=inferred_state,
            base_dir=base_dir,
            input_files=input_files,
            output_files=output_files,
            shp_layers=shp_layers,
            shp_crs=shp_crs,
            shp_attributes=shp_attributes,
        )

        with open(self.sc_markdown_path, mode='w') as f:
            f.write(result)

    def generate_sc_figure1(self):
        """
        Plot city and police precincts overlay
        """
        city = self.load_city_metadata()
        precincts = self.load_police_precincts()

        # set up common projection
        proj = util.crs.equal_area_from_geodf(city)
        city = city.to_crs(proj)
        precincts = precincts.to_crs(proj)

        Line2D = matplotlib.lines.Line2D
        Patch = matplotlib.patches.Patch

        # plot
        fig, ax = matplotlib.pyplot.subplots(figsize=(10, 10))

        city.plot(ax=ax, color='green', alpha=0.5)
        precincts.plot(ax=ax, color='none', edgecolor='black', alpha=0.75)

        legend_handles = [
            Patch(facecolor='green', alpha=0.5, label='City'),
            Line2D([0], [0], color='black', alpha=0.75,
                   lw=1, label='Precinct boundaries')
        ]
        ax.legend(handles=legend_handles, loc='lower right')

        ax.set_aspect('equal')
        ax.set_xlabel('Distance from center (mi)')
        ax.set_ylabel('Distance from center (mi)')
        ax.set_title("City and police precincts")

        matplotlib.pyplot.savefig(
            self.sc_figure1_path,
            bbox_inches='tight',
            dpi='figure',
        )

        # matplotlib keeps unclosed figures in the memory
        matplotlib.pyplot.close(fig)

    def generate_sc_figure2(self):
        """
        Plot police precincts over census tracts
        """
        tracts = self.load_census_tracts()
        precincts = self.load_police_precincts()

        # set up common projection
        proj = util.crs.equal_area_from_geodf(tracts)
        tracts = tracts.to_crs(proj)
        precincts = precincts.to_crs(proj)

        # plot
        fig, ax = matplotlib.pyplot.subplots(figsize=(10, 10))

        tracts.plot(ax=ax, color='green', edgecolor='white', alpha=0.5)
        precincts.plot(ax=ax, color='blue', edgecolor='black', alpha=0.5)

        Patch = matplotlib.patches.Patch
        legend_handles = [
            Patch(facecolor='green', alpha=0.5, label='Census tracts'),
            Patch(facecolor='blue', alpha=0.5, label='Police precincts'),
        ]
        ax.legend(handles=legend_handles, loc='lower right')

        ax.set_aspect('equal')
        ax.set_xlabel('Distance from center (mi)')
        ax.set_ylabel('Distance from center (mi)')
        ax.set_title("Police precincts over census tracts")

        matplotlib.pyplot.savefig(
            self.sc_figure2_path,
            bbox_inches='tight',
            dpi='figure',
        )

        matplotlib.pyplot.close(fig)

    def generate_sc_figure3(self):
        """
        Plot police precincts over block groups
        """
        bgs = self.load_block_groups()
        precincts = self.load_police_precincts()

        # set up common projection
        proj = util.crs.equal_area_from_geodf(bgs)
        bgs = bgs.to_crs(proj)
        precincts = precincts.to_crs(proj)

        # plot
        fig, ax = matplotlib.pyplot.subplots(figsize=(10, 10))

        bgs.plot(ax=ax, color='green', edgecolor='white', alpha=0.5)
        precincts.plot(ax=ax, color='blue', edgecolor='black', alpha=0.5)

        Patch = matplotlib.patches.Patch
        legend_handles = [
            Patch(facecolor='green', alpha=0.5, label='Block groups'),
            Patch(facecolor='blue', alpha=0.5, label='Police precincts'),
        ]
        ax.legend(handles=legend_handles, loc='lower right')

        ax.set_aspect('equal')
        ax.set_xlabel('Distance from center (mi)')
        ax.set_ylabel('Distance from center (mi)')
        ax.set_title("Police precincts over block groups")

        matplotlib.pyplot.savefig(
            self.sc_figure3_path,
            bbox_inches='tight',
            dpi='figure',
        )

        matplotlib.pyplot.close(fig)

    def generate_sc_figure4(self):
        """
        Plot police precincts over block groups (zoomed in)
        """
        bgs = self.load_block_groups()
        precincts = self.load_police_precincts()

        # set up common projection
        proj = util.crs.equal_area_from_geodf(precincts)
        bgs = bgs.to_crs(proj)
        precincts = precincts.to_crs(proj)

        # get bounds
        fig, ax = matplotlib.pyplot.subplots()
        precincts.plot(ax=ax)
        bounds = ax.axis()
        matplotlib.pyplot.close(fig)

        # plot
        fig, ax = matplotlib.pyplot.subplots(figsize=(10, 10))

        bgs.plot(ax=ax, color='green', edgecolor='white', alpha=0.5)
        precincts.plot(ax=ax, color='blue', edgecolor='black', alpha=0.5)

        Patch = matplotlib.patches.Patch
        legend_handles = [
            Patch(facecolor='green', alpha=0.5, label='Block groups'),
            Patch(facecolor='blue', alpha=0.5, label='Police precincts'),
        ]
        ax.legend(handles=legend_handles, loc='lower right')

        ax.set_aspect('equal')
        ax.axis(bounds)
        ax.set_xlabel('Distance from center (mi)')
        ax.set_ylabel('Distance from center (mi)')
        ax.set_title("Police precincts over block groups (zoomed in)")

        matplotlib.pyplot.savefig(
            self.sc_figure4_path,
            bbox_inches='tight',
            dpi='figure',
        )

        matplotlib.pyplot.close(fig)

    def generate_sc_figure5(self):
        """
        Plot population density at different levels
        """
        # load raw dataframes
        tracts = self.load_census_tracts()
        bgs = self.load_block_groups()
        precincts = self.load_police_precincts()

        # set up equal-area projection
        proj = util.crs.equal_area_from_geodf(precincts)
        tracts = tracts.to_crs(proj)
        bgs = bgs.to_crs(proj)
        precincts = precincts.to_crs(proj)

        # restrict areas to intersection (slow)
        _area = precincts.unary_union
        tracts = tracts[tracts.intersects(_area)]
        bgs = bgs[bgs.intersects(_area)]

        # calculate densities
        tracts['POPULATION_DENSITY'] = tracts['TOTAL_POPULATION'] / tracts.area
        bgs['POPULATION_DENSITY'] = bgs['TOTAL_POPULATION'] / bgs.area
        precincts['POPULATION_DENSITY'] = (
                precincts['TOTAL_POPULATION'] / precincts.area)

        # get bounds
        fig, ax = matplotlib.pyplot.subplots()
        precincts.plot(ax=ax)
        bounds = ax.axis()
        matplotlib.pyplot.close(fig)

        # plot
        fig, axes = matplotlib.pyplot.subplots(
            nrows=2,
            ncols=2,
            figsize=(10, 10),
        )
        axes[1][1].remove()

        # plot (by block group)
        ax = axes[0][0]
        bgs.plot(
            ax=ax,
            column='POPULATION_DENSITY',
            cmap='Blues',
            scheme='fisher_jenks',
            k=3,
            edgecolor=(0, 0, 0, 0.5),
            legend=True,
            legend_kwds={'loc': 'lower right'},
        )
        ax.set_aspect('equal')
        ax.axis(bounds)
        ax.set_xlabel('Distance from center (mi)')
        ax.set_ylabel('Distance from center (mi)')
        ax.set_title("Population density over block groups (/mi^2)")

        # plot (by census tract)
        ax = axes[0][1]
        tracts.plot(
            ax=ax,
            column='POPULATION_DENSITY',
            cmap='Blues',
            scheme='fisher_jenks',
            k=3,
            edgecolor=(0, 0, 0, 0.5),
            legend=True,
            legend_kwds={'loc': 'lower right'},
        )
        ax.set_aspect('equal')
        ax.axis(bounds)
        ax.set_xlabel('Distance from center (mi)')
        ax.set_ylabel('Distance from center (mi)')
        ax.set_title("Population density over census tracts (/mi^2)")

        # plot (by police precinct)
        ax = axes[1][0]
        precincts.plot(
            ax=ax,
            column='POPULATION_DENSITY',
            cmap='Blues',
            scheme='fisher_jenks',
            k=3,
            edgecolor=(0, 0, 0, 0.5),
            legend=True,
            legend_kwds={'loc': 'lower right'},
        )
        ax.set_aspect('equal')
        ax.set_xlabel('Distance from center (mi)')
        ax.set_ylabel('Distance from center (mi)')
        ax.set_title("Population density over police precincts (/mi^2)")

        # save
        matplotlib.pyplot.savefig(
            self.sc_figure5_path,
            bbox_inches='tight',
            dpi='figure',
        )

        matplotlib.pyplot.close(fig)

    # input

    def load_external_shapefile(self):
        path = str(self.spatial_input_dir)
        return util.io.load_shp(path)

    def load_preprocessed_shapefile(self):
        return util.io.load_zipshp(self.preprocessed_shapefile_path)

    def load_guessed_state(self):
        return util.io.load_json(self.guessed_state_path)

    def load_guessed_counties(self):
        return util.io.load_json(self.guessed_counties_path)

    def load_guessed_city(self):
        return util.io.load_json(self.guessed_city_path)

    def load_tract_values(self):
        return pandas.read_pickle(self.tract_values_path)

    def load_bg_values(self):
        return pandas.read_pickle(self.bg_values_path)

    def load_block_groups(self):
        return util.io.load_geojson(self.block_groups_path)

    def load_census_tracts(self):
        return util.io.load_geojson(self.census_tracts_path)

    def load_police_precincts(self):
        return util.io.load_geojson(self.police_precincts_path)

    def load_city(self):
        return util.io.load_geojson(self.city_path)

    def load_city_stats(self):
        obj = util.io.load_json(self.city_stats_path)
        ser = pandas.Series(obj)
        return ser

    # output

    def save_preprocessed_shapefile(self, df):
        util.io.save_zipshp(df, self.preprocessed_shapefile_path)

    def save_guessed_state(self, geoid):
        util.io.save_json(geoid, self.guessed_state_path)

    def save_guessed_counties(self, lst):
        util.io.save_json(lst, self.guessed_counties_path)

    def save_guessed_city(self, city_name):
        util.io.save_json(city_name, self.guessed_city_path)

    def save_tract_values(self, df):
        df.to_pickle(self.tract_values_path)

    def save_bg_values(self, df):
        df.to_pickle(self.bg_values_path)

    def save_block_groups(self, df):
        util.io.save_geojson(df, self.block_groups_path)

    def save_census_tracts(self, df):
        util.io.save_geojson(df, self.census_tracts_path)

    def save_police_precincts(self, df):
        util.io.save_geojson(df, self.police_precincts_path)

    def save_city(self, df):
        util.io.save_geojson(df, self.city_path)

    def save_city_stats(self, ser):
        obj = ser.to_dict()
        util.io.save_json(obj, self.city_stats_path)


class DepartmentFile(abc.ABC):
    """
    I represent a file specific to a department
    """

    @property
    def dependencies(self):
        """
        List of dependencies that are not the raw file itself
        """
        return []

    @property
    @abc.abstractmethod
    def raw_path(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def processed_path(self):
        raise NotImplementedError

    @abc.abstractmethod
    def load_raw(self):
        raise NotImplementedError

    @abc.abstractmethod
    def load_processed(self):
        raise NotImplementedError

    @abc.abstractmethod
    def process(self):
        raise NotImplementedError


class DepartmentCollection():
    """
    Represents a collection of all departments in the data
    """
    @property
    def path(self):
        return util.path.DATA_DIR / 'department'

    @property
    def input_path(self):
        return util.path.INPUT_DIR / 'department'

    @property
    def list_of_states_path(self):
        return self.path / 'list_of_states.json'

    # util

    def list(self):
        # use the input directory only, as this is a dependency for
        # creating the other directories at prepare.py
        names = [x.name for x in self.input_path.iterdir() if x.is_dir()]
        return [Department(name) for name in sorted(names)]

    # doit actions

    def create_list_of_states(self):
        """
        Create a list of states where the departments are

        (to later retrieve census tracts from those)
        """
        states = [dept.load_guessed_state() for dept in self.list()]
        states = set(states)
        states = sorted(states)
        self.save_list_of_states(states)

    # input/output

    def load_list_of_states(self):
        return util.io.load_json(self.list_of_states_path)

    def save_list_of_states(self, lst):
        util.io.save_json(lst, self.list_of_states_path)


def list_states():
    """
    Returns a list with all states where the departments are
    """
    dept_coll = DepartmentCollection()
    return dept_coll.load_list_of_states()
