"""
Module for defining doit tasks

Before running this, make sure to run the preparation tasks before:

>>> doit -f prepare.py
"""

from shutil import copyfile, copytree

import doit
import doit.tools

from cpe_help import Census, Department, DepartmentColl, list_departments, list_states
from cpe_help.util.doit_tasks import TaskHelper
from cpe_help.util.path import (
    DATA_DIR,
    maybe_rmtree,
)


KAGGLE_ZIPFILE = DATA_DIR / 'inputs' / 'data-science-for-good.zip'


def _copyfile(src, dst, **kwargs):
    """
    Copy file from src to dst, creting dirs if needed
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    copyfile(src, dst, **kwargs)


def _copytree(src, dst, **kwargs):
    """
    Recursively copy an entire directory tree rooted at src

    If dst already exists, it will be completely removed before copying.
    """
    # remove directory, if it exists
    maybe_rmtree(dst)

    # copy directory
    copytree(src, dst, **kwargs)


def task_download_state_boundaries():
    """
    Download state boundaries from the ACS website
    """
    census = Census()
    file = census.state_boundaries_path
    return {
        'targets': [file],
        'actions': [census.download_state_boundaries],
        'uptodate': [True],
    }


def task_download_extra():
    # just a prototype for other data that may be retrieved
    yield TaskHelper.download(
        'https://data.austintexas.gov/api/views/u2k2-n8ez/rows.csv?accessType=DOWNLOAD',
        Department('37-00027').raw_path / 'OIS.csv',
        name='austin_ois',
    )

    # yield TaskHelper.download(
    #     'https://data.austintexas.gov/api/views/g3bw-w7hh/rows.csv?accessType=DOWNLOAD',
    #     Department('37-00027').raw_path / 'crime_reports.csv',
    #     name='austin_crimes',
    # )


def task_spread_acs_tables():
    """
    Spread American Community Survey tables into departments dirs
    """
    dept_dirs = [x
                 for x in (DATA_DIR / 'inputs' / 'cpe-data').iterdir()
                 if x.is_dir()]

    for dept_dir in dept_dirs:
        name = dept_dir.name[5:]
        dept = Department(name)
        # NOTE: do not use the next built-in here. doit will catch
        #       and StopIteraction exception in a weird place and
        #       complicate debugging
        src_dir = dept_dir / f"{name}_ACS_data"
        dst_dir = dept.external_acs_path
        src_files = [list(x.glob('*_with_ann.csv'))[0]
                     for x in src_dir.iterdir()
                     if x.is_dir()]
        dst_files = [dst_dir / x.name for x in src_files]

        yield {
            'name': name,
            'file_dep': src_files,
            'targets': dst_files,
            'actions': [(_copyfile, [src, dst])
                        for src, dst in zip(src_files, dst_files)],
            # TODO: rmtree(dst_dir)
            'clean': True,
        }


def task_spread_shapefiles():
    """
    Spread district shapefiles into departments directories
    """
    dept_dirs = [x
                 for x in (DATA_DIR / 'inputs' / 'cpe-data').iterdir()
                 if x.is_dir()]

    for dept_dir in dept_dirs:
        name = dept_dir.name[5:]
        dept = Department(name)
        src_dir = dept_dir / f"{name}_Shapefiles"
        dst_dir = dept.external_shapefile_path
        src_files = list(src_dir.iterdir())
        dst_files = [dst_dir / x.name for x in src_files]

        yield {
            'name': name,
            'file_dep': src_files,
            'targets': dst_files,
            'actions': [(_copytree, [src_dir, dst_dir])],
            'clean': True,
        }


def task_spread_other():
    """
    Spread unattached files into departments directories
    """
    dept_dirs = [x
                 for x in (DATA_DIR / 'inputs' / 'cpe-data').iterdir()
                 if x.is_dir()]

    for dept_dir in dept_dirs:
        name = dept_dir.name[5:]
        dept = Department(name)
        src_files = [x for x in dept_dir.iterdir() if x.is_file()]
        dst_files = [dept.external_path / x.name for x in src_files]

        yield {
            'name': name,
            'file_dep': src_files,
            'targets': dst_files,
            'actions': [(_copyfile, [src, dst])
                        for src, dst in zip(src_files, dst_files)],
            'clean': True,
        }


def task_guess_states():
    """
    Guess the state for each department
    """
    census = Census()
    for dept in list_departments():
        yield {
            'name': dept.name,
            'file_dep': [
                census.state_boundaries_path,
                dept.preprocessed_shapefile_path,
            ],
            'targets': [dept.guessed_state_path],
            'actions': [dept.guess_state],
            'clean': [dept.remove_guessed_state],
        }


def task_create_list_of_states():
    """
    Unite the guessed states for each department
    """
    dept_coll = DepartmentColl()
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
            'file_dep': [KAGGLE_ZIPFILE],
            'task_dep': ['spread_shapefiles'],
            'targets': [dept.preprocessed_shapefile_path],
            'actions': [dept.preprocess_shapefile],
            'clean': [dept.remove_preprocessed_shapefile],
        }


@doit.create_after('create_list_of_states')
def task_download_tract_boundaries():
    """
    Download census tract boundaries for each state
    """
    census = Census()
    for state in list_states():
        yield {
            'name': state,
            'actions': [(census.download_tract_boundaries, (state,))],
            'targets': [census.tract_boundaries_path(state)],
            'uptodate': [doit.tools.run_once],
        }
