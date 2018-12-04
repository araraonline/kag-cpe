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


def task_city():
    """
    Output statistics for each department city
    """
    for dept in Department.list():
        yield {
            'name': dept.name,
            'file_dep': [dept.city_path],
            'targets': [dept.city_output],
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


# sanity check

def task_generate_sc_markdown():
    """
    Generate sanity check md files for each department
    """
    for dept in Department.list():
        yield {
            'name': dept.name,
            'file_dep': [],
            'targets': [dept.sc_markdown_path],
            'actions': [dept.generate_sc_markdown],
            'clean': True,
        }


def task_generate_sc_html():
    """
    Generate sanity check html files for each department
    """
    for dept in Department.list():
        command = (f"pandoc --self-contained"
                   f" -o {dept.sc_html_path}"
                   f" {dept.sc_markdown_path}")

        yield {
            'name': dept.name,
            'file_dep': [
                dept.sc_figure1_path,
                dept.sc_figure2_path,
                dept.sc_figure3_path,
                dept.sc_figure4_path,
                dept.sc_figure5_path,
                dept.sc_markdown_path,
            ],
            'targets': [dept.sc_html_path],
            'actions': [command],
            'clean': True,
        }


def task_generate_sc_figure1():
    """
    Generate figure #1 for the sanity check of each department
    """
    for dept in Department.list():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.guessed_city_path,
                dept.police_precincts_path,
            ],
            'task_dep': ['download_place_boundaries'],
            'targets': [dept.sc_figure1_path],
            'actions': [dept.generate_sc_figure1],
            'clean': True,
        }


def task_generate_sc_figure2():
    """
    Generate figure #2 for the sanity check of each department
    """
    for dept in Department.list():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.census_tracts_path,
                dept.police_precincts_path,
            ],
            'targets': [dept.sc_figure2_path],
            'actions': [dept.generate_sc_figure2],
            'clean': True,
        }


def task_generate_sc_figure3():
    """
    Generate figure #3 for the sanity check of each department
    """
    for dept in Department.list():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.block_groups_path,
                dept.police_precincts_path,
            ],
            'targets': [dept.sc_figure3_path],
            'actions': [dept.generate_sc_figure3],
            'clean': True,
        }


def task_generate_sc_figure4():
    """
    Generate figure #4 for the sanity check of each department
    """
    for dept in Department.list():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.block_groups_path,
                dept.police_precincts_path,
            ],
            'targets': [dept.sc_figure4_path],
            'actions': [dept.generate_sc_figure4],
            'clean': True,
        }


def task_generate_sc_figure5():
    """
    Generate figure #5 for the sanity check of each department
    """
    for dept in Department.list():
        yield {
            'name': dept.name,
            'file_dep': [
                dept.census_tracts_path,
                dept.block_groups_path,
                dept.police_precincts_path,
            ],
            'targets': [dept.sc_figure5_path],
            'actions': [dept.generate_sc_figure5],
            'clean': True,
        }
