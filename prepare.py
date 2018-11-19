"""
Preparation tasks for doit

The tasks present here are required for the creation of tasks in the
main dodo.py file.
"""

import shutil

import doit
import doit.tools

from cpe_help import Department, util
from cpe_help.tiger import get_tiger
from cpe_help.util.path import (
    DATA_DIR,
    maybe_mkdir,
)


BASE_DIRECTORIES = [
    DATA_DIR / 'kaggle',
    DATA_DIR / 'input',
    DATA_DIR / 'input' / 'department',

    DATA_DIR / 'departments',
    DATA_DIR / 'tiger',
]

KAGGLE_DIR = DATA_DIR / 'kaggle'
CPE_DATA_DIR = KAGGLE_DIR / 'cpe-data'
KAGGLE_ZIPFILE = KAGGLE_DIR / 'cpe-data.zip'


# helper/actions

class InputDepartment():
    """
    I represent a raw Department (that came directly from Kaggle data)
    """

    @property
    def path(self):
        return CPE_DATA_DIR / f'Dept_{self.name}'

    @property
    def acs_path(self):
        return self.path / f'{self.name}_ACS_data'

    @property
    def shp_path(self):
        return self.path / f'{self.name}_Shapefiles'

    @property
    def acs_files(self):
        return list(self.acs_path.glob(f'**/*_with_ann.csv'))

    @property
    def other_files(self):
        return [x for x in self.path.iterdir() if x.is_file()]

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'InputDepartment(name={self.name!r})'

    def to_department(self):
        return Department(self.name)

    def spread_files(self):
        """
        Spread my files to the (department) working directory

        ACS data is being retrieved programatically, so, I will ignore
        ACS files.
        """
        dst = self.to_department()

        # copy shapefiles
        src_shapefile = self.shp_path
        dst_shapefile = dst.spatial_input_dir
        util.path.maybe_rmtree(dst_shapefile)
        shutil.copytree(src_shapefile, dst_shapefile)

        # copy other files
        for file in self.other_files:
            shutil.copy(file, dst.tabular_input_dir)

    @classmethod
    def from_path(cls, path):
        return InputDepartment(path.name[5:])

    @classmethod
    def list(cls):
        return [cls.from_path(x)
                for x in CPE_DATA_DIR.iterdir()
                if x.is_dir()]


def create_base_directories():
    """
    Create base data directories
    """
    for dir in BASE_DIRECTORIES:
        maybe_mkdir(dir)


# basic tasks

def task_create_base_directories():
    """
    Create base data directories
    """
    return {
        'targets': BASE_DIRECTORIES,
        'actions': [create_base_directories],
        'uptodate': [True],
    }


# tiger tasks

@doit.create_after('create_base_directories')
def task_create_tiger_directories():
    """
    Create TIGER's directories
    """
    tiger = get_tiger()
    return {
        'targets': tiger.directories,
        'actions': [tiger.create_directories],
        'uptodate': [True],
    }


# department tasks

@doit.create_after('create_base_directories')
def task_create_department_directories():
    """
    Create departments' directories
    """
    depts = InputDepartment.list()
    depts = [d.to_department() for d in depts]
    for dept in depts:
        yield {
            'name': dept.name,
            'targets': dept.directories,
            'actions': [dept.create_directories],
            'uptodate': [True],
        }


@doit.create_after('create_department_directories')
def task_spread_department_data():
    """
    Spread department data from inputs to working directory
    """
    for dept in InputDepartment.list():
        # task will always run
        # I don't want to set up complex file handling now
        # may change when dealing with 'clean'
        yield {
            'name': dept.name,
            'actions': [dept.spread_files],
        }
