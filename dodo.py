"""
Module for defining doit tasks
"""

from shutil import copyfile, copytree, rmtree

from doit import create_after

from cpe_help.department import Department
from cpe_help.util.path import DATA_DIR


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


def downloader(url, target, force=False, name=None):
    """
    Generate a new task to download a file from url to target

    Create dirs if needed.

    Parameters
    ----------
    url : str
        The url to download from.
    target : Path
        The path the file will be saved to.
    force : bool, default False
        If True, forces download even if the file is already present
        (replacing the file).
    name : str, default None
        If specified, the name of the task to be run.

    Returns
    -------
    dict
        The task to be performed.
    """
    target.parent.mkdir(parents=True, exist_ok=True)

    task = {
        'targets': [target],
        'actions': [f"python -m cpe_help.util.download '{url}' '{target}'"],
        'uptodate': [not force],
    }

    if name:
        task['name'] = name

    return task


def unzipper(src, dst, name=None):
    """
    Generate a new task to unzip a file to a specific location

    Parameters
    ----------
    src : Path
        Location of the .zip file.
    dst : Path
        Directory to extract files to.
    name : str, default None
        If specified, the name of the task to be run.

    Returns
    -------
    dict
        The task to be performed.
    """
    task = {
        'file_dep': [src],
        'targets': [dst],
        'actions': [

            # XXX: This is a hack... rmtree below needs the file to exist,
            # XXX: otherwise it will break.
            # XXX: Need to think of cases where directory is automatically
            # XXX: created or not better.
            (dst.mkdir, [], {'parents': True, 'exist_ok': True}),
            (rmtree, [dst]),
            f"unzip {src} -d {dst}",
        ],
    }

    if name:
        task['name'] = name

    return task


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
    return unzipper(
        DATA_DIR / 'inputs' / 'data-science-for-good.zip',
        DATA_DIR / 'inputs' / 'cpe-data',
    )


@create_after('unzip_inputs')
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
        # TODO: There are some fixes in the code below
        # NOTE: do not use the next built-in here. doit will catch
        #       and StopIteraction exception in a weird place and
        #       complicate debugging
        src_dir = list(dept_dir.glob(f"{name}_ACS?data"))[0]  # FIX: glob
        dst_dir = dept.dir / 'external' / 'ACS'
        src_files = [list(x.glob('*_with_ann.csv'))[0]
                     for x in src_dir.iterdir()
                     if x.is_dir() and any(x.iterdir())]  # FIX: iterdir
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


@create_after('unzip_inputs')
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
        dst_dir = dept.dir / 'external' / 'shapefiles'
        src_files = list(src_dir.iterdir())
        dst_files = [dst_dir / x.name for x in src_files]

        yield {
            'name': name,
            'file_dep': src_files,
            'targets': dst_files,
            'actions': [(_copytree, [src_dir, dst_dir])],
            'clean': True,
        }


@create_after('unzip_inputs')
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
        dst_files = [dept.dir / 'external' / x.name for x in src_files]

        yield {
            'name': name,
            'file_dep': src_files,
            'targets': dst_files,
            'actions': [(_copyfile, [src, dst])
                        for src, dst in zip(src_files, dst_files)],
            'clean': True,
        }


def task_fetch_census_geography():
    # TODO: automatically retrieve

    # XXX: Shapefile below is simplified
    yield downloader(
        'https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_25_tract_500k.zip',
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'massachusetts.zip',
        name='massachusetts',
    )

    yield downloader(
        'https://www2.census.gov/geo/tiger/TIGER2015/TRACT/tl_2015_48_tract.zip',
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'texas.zip',
        name='texas',
    )


def task_unzip_census_geography():
    yield unzipper(
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'massachusetts.zip',
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'massachusetts',
        name='massachusetts',
    )

    yield unzipper(
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'texas.zip',
        DATA_DIR / 'census' / '2015' / 'shapefiles' / 'texas',
        name='texas',
    )


def task_download_extra():
    # just a prototype for other data that may be retrieved
    yield downloader(
        'https://data.austintexas.gov/api/views/u2k2-n8ez/rows.csv?accessType=DOWNLOAD',
        Department('37-00027').dir / 'raw' / 'OIS.csv',
        name='austin_ois',
    )

    yield downloader(
        'https://data.austintexas.gov/api/views/g3bw-w7hh/rows.csv?accessType=DOWNLOAD',
        Department('37-00027').dir / 'raw' / 'crime_reports.csv',
        name='austin_crimes',
    )