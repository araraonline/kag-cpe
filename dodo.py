"""
Module for defining doit tasks

Before running this, make sure to run the preparation tasks before:

>>> doit -f prepare.py
"""

import doit
import doit.tools

from cpe_help import (
    Department,
    DepartmentCollection,
    list_departments,
    list_states,
)
from cpe_help.tiger import get_tiger
from cpe_help.util.doit_tasks import TaskHelper


def task_download_state_boundaries():
    """
    Download state boundaries from the ACS website
    """
    tiger = get_tiger()
    file = tiger.state_boundaries_path
    return {
        'targets': [file],
        'actions': [tiger.download_state_boundaries],
        'uptodate': [True],
    }


def task_download_county_boundaries():
    """
    Download county boundaries from the TIGER shapefiles
    """
    tiger = get_tiger()
    file = tiger.county_boundaries_path
    return {
        'targets': [file],
        'actions': [tiger.download_county_boundaries],
        'uptodate': [doit.tools.run_once],
    }


def task_download_extra():
    # just a prototype for other data that may be retrieved
    yield TaskHelper.download(
        'https://data.austintexas.gov/api/views/u2k2-n8ez/rows.csv?accessType=DOWNLOAD',
        Department('37-00027').raw_dir / 'OIS.csv',
        name='austin_ois',
    )

    yield TaskHelper.download(
        'https://www2.census.gov/programs-surveys/acs/replicate_estimates/2016/data/5-year/140/B01001_25.csv.gz',
        get_tiger().path / 'sample_vrt.csv.gz',
        name='variance_rep_table',
    )

    # yield TaskHelper.download(
    #     'https://data.austintexas.gov/api/views/g3bw-w7hh/rows.csv?accessType=DOWNLOAD',
    #     Department('37-00027').raw_dir / 'crime_reports.csv',
    #     name='austin_crimes',
    # )


def task_guess_states():
    """
    Guess the state for each department
    """
    tiger = get_tiger()
    for dept in list_departments():
        yield {
            'name': dept.name,
            'file_dep': [
                tiger.state_boundaries_path,
                dept.preprocessed_shapefile_path,
            ],
            'targets': [dept.guessed_state_path],
            'actions': [dept.guess_state],
            'clean': [dept.remove_guessed_state],
        }


def task_guess_counties():
    """
    Guess the counties that compose each police department

    The city surrounding each police department is also taken into
    account.
    """
    for dept in list_departments():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.guessed_city_path,
                dept.preprocessed_shapefile_path,
            ],
            'task_dep': [
                'download_place_boundaries',
                'download_county_boundaries',
            ],
            'targets': [dept.guessed_counties_path],
            'actions': [dept.guess_counties],
            'clean': [dept.remove_guessed_counties],
        }


def task_guess_cities():
    """
    Guess the city of each department
    """
    for dept in list_departments():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.preprocessed_shapefile_path,
                dept.guessed_state_path,
            ],
            'task_dep': ['download_place_boundaries'],
            'targets': [dept.guessed_city_path],
            'actions': [dept.guess_city],
            'clean': [dept.remove_guessed_city],
        }


def task_create_list_of_states():
    """
    Unite the guessed states for each department
    """
    dept_coll = DepartmentCollection()
    return {
        'file_dep': [dept.guessed_state_path for dept in list_departments()],
        'targets': [dept_coll.list_of_states_path],
        'actions': [dept_coll.create_list_of_states],
        'clean': [dept_coll.remove_list_of_states],
    }


def task_preprocess_shapefiles():
    for dept in list_departments():
        yield {
            'name': dept.name,
            # TODO: arrange dependencies
            # TODO: remove uptodate
            'targets': [dept.preprocessed_shapefile_path],
            'actions': [dept.preprocess_shapefile],
            'clean': [dept.remove_preprocessed_shapefile],
            'uptodate': [True],
        }


def task_download_tract_values():
    """
    Download census tract values for each department
    """
    for dept in list_departments():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.guessed_state_path,
                dept.guessed_counties_path,
            ],
            'targets': [dept.tract_values_path],
            'actions': [dept.download_tract_values],
            'clean': [dept.remove_tract_values],
        }


def task_download_bg_values():
    for dept in list_departments():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.guessed_state_path,
                dept.guessed_counties_path,
            ],
            'targets': [dept.bg_values_path],
            'actions': [dept.download_bg_values],
            'clean': [dept.remove_bg_values],
        }


@doit.create_after('create_list_of_states')
def task_download_tract_boundaries():
    """
    Download census tract boundaries for each state
    """
    tiger = get_tiger()
    for state in list_states():
        yield {
            'name': state,
            'actions': [(tiger.download_tract_boundaries, (state,))],
            'targets': [tiger.tract_boundaries_path(state)],
            'uptodate': [doit.tools.run_once],
        }


@doit.create_after('create_list_of_states')
def task_download_bg_boundaries():
    """
    Download block group boundaries for each relevant state
    """
    tiger = get_tiger()
    for state in list_states():
        yield {
            'name': state,
            'actions': [(tiger.download_bg_boundaries, (state,))],
            'targets': [tiger.bg_boundaries_path(state)],
            'uptodate': [doit.tools.run_once],
        }


@doit.create_after('create_list_of_states')
def task_download_place_boundaries():
    """
    Download place boundaries for each relevant state
    """
    tiger = get_tiger()
    for state in list_states():
        yield {
            'name': state,
            'actions': [(tiger.download_place_boundaries, (state,))],
            'targets': [tiger.place_boundaries_path(state)],
            'uptodate': [doit.tools.run_once],
        }


def task_process_census_tracts():
    """
    Merge census tract values with census tract boundaries
    """
    for dept in list_departments():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.guessed_state_path,
                dept.guessed_counties_path,
                dept.tract_values_path,
            ],
            'task_dep': ['download_tract_boundaries'],
            'targets': [dept.census_tracts_path],
            'actions': [dept.process_census_tracts],
            'clean': [dept.remove_census_tracts],
        }


def task_process_block_groups():
    """
    Merge block group values with block group boundaries
    """
    for dept in list_departments():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.guessed_state_path,
                dept.guessed_counties_path,
                dept.bg_values_path,
            ],
            'task_dep': ['download_bg_boundaries'],
            'targets': [dept.block_groups_path],
            'actions': [dept.process_block_groups],
            'clean': [dept.remove_block_groups],
        }


def task_process_police_precincts():
    """
    Process police precincts data
    """
    for dept in list_departments():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.block_groups_path,
                dept.preprocessed_shapefile_path,
            ],
            'targets': [dept.police_precincts_path],
            'actions': [dept.process_police_precincts],
            'clean': [dept.remove_police_precincts],
        }


def task_preprocess_4900033_arrests():
    """
    Preprocess arrests data for Department 49-00033
    """
    dept = Department('49-00033')
    return {
        'file_dep': [dept.external_arrests_path],
        'targets': [dept.preprocessed_arrests_path],
        'actions': [dept.preprocess_arrests],
        'clean': [dept.remove_preprocessed_arrests],
    }


def task_generate_city_stats():
    """
    Generate statistics for the city of each department
    """
    for dept in list_departments():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.guessed_city_path,
                dept.block_groups_path,
            ],
            'task_dep': ['download_place_boundaries'],
            'targets': [dept.city_stats_path],
            'actions': [dept.generate_city_stats],
            'clean': [dept.remove_city_stats],
        }


# import output tasks
# leave this at the end of the file
from output import *
