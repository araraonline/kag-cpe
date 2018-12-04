"""
General preparation tasks for doit

Run this before the main dodo.py file.
"""

from cpe_help import (
    Department,
    TIGER,
    util,
)


DATA_DIR = util.path.DATA_DIR


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
