"""
Preparation tasks for inputs coming from Kaggle

See also:

prepare.py
"""

import shutil

import doit

from cpe_help import Department, TIGER, util


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
CPE_DATA_ZIP = KAGGLE_DIR / 'cpe-data.zip'
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
        return f'KaggleDepartment(name={self.name!r})'

    def spread_inputs(self):
        """
        Spread my files to the department input directory

        ACS data is being retrieved programatically, so, I will ignore
        them.
        """
        dst = Department(self.name)

        # copy shapefiles
        src_shapefile = self.shp_path
        dst_shapefile = dst.spatial_input_dir
        util.file.maybe_rmtree(dst_shapefile)
        shutil.copytree(src_shapefile, dst_shapefile)

        # copy tabular files
        util.file.maybe_mkdir(dst.tabular_input_dir)
        for file in self.other_files:
            shutil.copy(file, dst.tabular_input_dir)

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
def task_unzip_kaggle_inputs():
    """
    Unzip the Kaggle inputs file
    """
    return util.TaskHelper.unzip(CPE_DATA_ZIP, CPE_DATA_DIR)


@doit.create_after('unzip_kaggle_inputs')
def task_spread_kaggle_inputs():
    """
    Spread Kaggle files into the input directory
    """
    for dept in KaggleDepartment.list():
        yield {
            'name': dept.name,
            'actions': [dept.spread_inputs],
        }


@doit.create_after('spread_kaggle_inputs')
def task_create_department_directories():
    """
    Create departments' directories
    """
    for dept in Department.list():
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
    tiger = TIGER()
    return {
        'targets': tiger.directories,
        'actions': [tiger.create_directories],
        'uptodate': [True],
    }
