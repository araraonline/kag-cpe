"""
Preparation tasks for doit

The tasks present here are required for the creation of tasks in the
main dodo.py file.
"""

import doit.tools

from cpe_help import Department, util
from cpe_help.tiger import get_tiger


DATA_DIR = util.path.DATA_DIR
BASE_DIRECTORIES = [
    # TODO: think about these

    DATA_DIR / 'kaggle',

    DATA_DIR / 'input',
    DATA_DIR / 'input' / 'department',

    DATA_DIR / 'output',
    DATA_DIR / 'output' / 'department',

    DATA_DIR / 'department',
    DATA_DIR / 'tiger',
]

KAGGLE_DIR = DATA_DIR / 'kaggle'
CPE_DATA_DIR = KAGGLE_DIR / 'cpe-data'


class KaggleDepartment():
    """
    I represent a Department that came directly from Kaggle data
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

    @classmethod
    def from_path(cls, path):
        return cls(path.name[5:])

    @classmethod
    def list(cls):
        return [cls.from_path(x)
                for x in CPE_DATA_DIR.iterdir()
                if x.is_dir()]


def _create_base_directories():
    """
    Create base data directories
    """
    for dir in BASE_DIRECTORIES:
        util.file.maybe_mkdir(dir)


def task_create_base_directories():
    """
    Create base data directories
    """
    return {
        'targets': BASE_DIRECTORIES,
        'actions': [_create_base_directories],
        'uptodate': [True],
    }


@doit.create_after('create_base_directories')
def spread_kaggle_inputs():
    """
    Spread Kaggle files into the input directory
    """
    raise NotImplementedError


@doit.create_after('create_base_directories')
def task_create_department_directories():
    """
    Create departments' directories
    """
    depts = Department.list()
    for dept in depts:
        yield {
            'name': dept.name,
            'targets': dept.directories,
            'actions': [dept.create_directories],
            'uptodate': [True],
        }


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
