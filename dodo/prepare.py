"""
This is a doit script for preparing for the next doit.

While creating tasks for this project, lots (close to all) tasks depend
on the listing of departments. However, this list is just created after
the Kaggle inputs are prepared (may be created manually by CPE later),
so, we separate the preparation here so that doit can do its job in
matching targets to dependencies.

Run this by:

>>> doit -f prepare_inputs.py
"""

import doit.tools

from cpe_help import DepartmentColl
from cpe_help.util.doit_tasks import TaskHelper
from cpe_help.util.path import (
    DATA_DIR,
    maybe_rmtree,
)


KAGGLE_ZIPFILE = DATA_DIR / 'inputs' / 'data-science-for-good.zip'


def task_download_inputs():
    """
    Retrieve raw departments data from Kaggle
    """
    return {
        'actions': [[
            'kaggle',
            'datasets',
            'download',
            '-d',
            'center-for-policing-equity/data-science-for-good',
            '-p',
            'data/inputs'
        ]],
        'targets': [KAGGLE_ZIPFILE],
        'uptodate': [doit.tools.run_once],
    }


def task_unzip_inputs():
    """
    Unzip raw departments data from Kaggle
    """
    return TaskHelper.unzip(
        KAGGLE_ZIPFILE,
        DATA_DIR / 'inputs' / 'cpe-data',
    )


def task_create_dept_list():
    """
    Create a list of available departments
    """
    dept_coll = DepartmentColl()
    return {
        'file_dep': [KAGGLE_ZIPFILE],
        'task_dep': ['unzip_inputs'],
        'targets': [dept_coll.list_of_departments_path],
        'actions': [dept_coll.create_list_of_departments],
        'clean': [dept_coll.remove_list_of_departments],
    }
