"""
dodo file for generating outputs

This should not be run directly. Instead, all tasks here are imported at
the main dodo.py file and will be run there.
"""

from cpe_help import Department


def task_output_city_stats():
    """
    Output city stats for each department
    """
    for dept in Department.list():
        yield {
            'name': dept.name,
            'file_dep': [dept.city_stats_path],
            'targets': [dept.city_stats_output],
            'actions': ['cp %(dependencies)s %(targets)s'],
            'clean': True,
        }


def task_output_census_tracts():
    """
    Output census tracts for each department
    """
    for dept in Department.list():
        yield {
            'name': dept.name,
            'file_dep': [dept.census_tracts_path],
            'targets': [dept.census_tracts_output],
            'actions': ['cp %(dependencies)s %(targets)s'],
            'clean': True,
        }


def task_output_block_groups():
    """
    Output block groups for each department
    """
    for dept in Department.list():
        yield {
            'name': dept.name,
            'file_dep': [dept.block_groups_path],
            'targets': [dept.block_groups_output],
            'actions': ['cp %(dependencies)s %(targets)s'],
            'clean': True,
        }


def task_output_police_precincts():
    """
    Output police precincts for each department
    """
    for dept in Department.list():
        yield {
            'name': dept.name,
            'file_dep': [dept.police_precincts_path],
            'targets': [dept.police_precincts_output],
            'actions': ['cp %(dependencies)s %(targets)s'],
            'clean': True,
        }


def task_process_department_files():
    """
    Preprocess individual files for departments
    """
    for dept in Department.list():
        for file_name, file in dept.files.items():
            yield {
                'name': f'{dept}:{file_name}',
                'file_dep': [file.raw_path] + file.dependencies,
                'targets': [file.processed_path],
                'actions': [file.process],
                'clean': True,
            }
