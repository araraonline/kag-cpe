"""
Module for defining doit tasks
"""

from os import remove as rmfile
from shutil import copyfile, copytree, rmtree

from doit import create_after

from cpe_help import Census, Department, list_departments
from cpe_help.util.path import DATA_DIR, maybe_mkdir, maybe_rmfile, maybe_rmtree


class TaskHelper(object):
    """
    I help with the creation of tasks
    """
    @staticmethod
    def download(url, out, overwrite=False, **kwargs):
        """
        Generate a task to download a file

        Parameters
        ----------
        url : str
            The url to download from.
        out : str or Path
            The output filename.
        overwrite : bool, default False
            If True, overwrite existing files. Otherwise, do not perform
            the download when out exists.
        kwargs
            Keyword arguments are added as items of the resulting dict.

        Returns
        -------
        dict
            The task to be performed.
        """
        from cpe_help.util.download import download
        task = {
            'targets': [out],
            'actions': [(download, (url, out))],
            'uptodate': [not overwrite],
        }
        task.update(kwargs)
        return task

    @staticmethod
    def unzip(file, dir, **kwargs):
        """
        Generate a task to extract files from a ZIP archive

        Parameters
        ----------
        file : str or Path
            The input ZIP file.
        dir : str or Path
            The directory to extract the ZIP contents to.
        kwargs
            Keyword arguments are added as items of the resulting dict.

        Returns
        -------
        dict
            The task to be performed.

        Notes
        -----
        As we can't know the ZIP archive contents beforehand, this task
        will only be rerun when the whole output directory goes missing
        (not its contents).
        """
        from cpe_help.util.compression import unzip
        task = {
            'file_dep': [file],
            'targets': [dir],
            'actions': [(unzip, (file, dir))],
            'clean': [(rmtree, (dir,))],
        }
        task.update(kwargs)
        return task


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
    try:
        rmtree(dst)
    except FileNotFoundError:
        pass

    # copy directory
    copytree(src, dst, **kwargs)


def task_fetch_inputs():
    """
    Retrieve raw departments data from Kaggle
    """
    return {
        'actions': [
            'kaggle datasets download -d center-for-policing-equity/data-science-for-good -p data/inputs',
        ],
        'targets': [
            DATA_DIR / 'inputs' / 'data-science-for-good.zip',
        ],

        # force doit to always mark the task
        # as up-to-date (unless no targets found)
        'uptodate': [True],
    }


def task_unzip_inputs():
    """
    Unzip raw departments data from Kaggle
    """
    return TaskHelper.unzip(
        DATA_DIR / 'inputs' / 'data-science-for-good.zip',
        DATA_DIR / 'inputs' / 'cpe-data',
    )


@create_after('unzip_inputs')
def task_create_dirs():
    """
    Create a dir for each department in the inputs

    Necessary for running list_departments().
    """
    dept_dirs = [x
                 for x in (DATA_DIR / 'inputs' / 'cpe-data').iterdir()
                 if x.is_dir()]

    for dept_dir in dept_dirs:
        name = dept_dir.name[5:]
        dept = Department(name)
        yield {
            'name': name,
            'file_dep': [DATA_DIR / 'inputs' / 'data-science-for-good.zip'],
            'targets': [dept.path],
            'actions': [(maybe_mkdir, (dept.path,))],
            'clean': [(maybe_rmtree, (dept.path,))],
        }


@create_after('create_dirs')
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


@create_after('create_dirs')
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


@create_after('create_dirs')
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


@create_after('create_dirs')
def task_guess_states():
    """
    Guess the state for each department
    """
    census = Census()
    for dept in list_departments():
        yield {
            'file_dep': [
                census.state_boundaries_zip_path,
                dept.preprocessed_shapefile_path,
            ],
            'targets': [dept.guessed_state_path],
            'actions': [dept.guess_state],
            'clean': True,
        }


@create_after('spread_shapefiles')
def task_preprocess_shapefiles():
    extensions = ['cpg', 'dbf', 'prj', 'shp', 'shx']

    for dept in list_departments():
        src = dept.external_shapefile_path
        dst = dept.preprocessed_shapefile_path
        yield {
            'name': dept.name,
            'file_dep': [x for x in src.iterdir()],
            'targets': [dst],
            'actions': [dept.preprocess_shapefile],
            'clean': [f'rm -rf {dept.preprocessed_shapefile_path}'],
        }


def task_fetch_census_geography():
    # TODO: automatically retrieve

    # XXX: Shapefile below is simplified
    yield TaskHelper.download(
        'https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_25_tract_500k.zip',
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'massachusetts.zip',
        name='massachusetts',
    )

    yield TaskHelper.download(
        'https://www2.census.gov/geo/tiger/TIGER2015/TRACT/tl_2015_48_tract.zip',
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'texas.zip',
        name='texas',
    )


def task_unzip_census_geography():
    yield TaskHelper.unzip(
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'massachusetts.zip',
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'massachusetts',
        name='massachusetts',
    )

    yield TaskHelper.unzip(
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'texas.zip',
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'texas',
        name='texas',
    )


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


def task_download_state_boundaries():
    """
    Download state boundaries from the ACS website
    """
    census = Census()
    zipfile = census.state_boundaries_zip_path
    directory = census.state_boundaries_shp_path
    return {
        'targets': [zipfile, directory],
        'actions': [census.download_state_boundaries],
        'uptodate': [True],
        'clean': [(maybe_rmfile, (zipfile,)),
                  (maybe_rmtree, (directory,))],
    }
