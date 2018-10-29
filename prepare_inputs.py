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
from cpe_help.util.path import (
    DATA_DIR,
    maybe_rmtree,
)


KAGGLE_ZIPFILE = DATA_DIR / 'inputs' / 'data-science-for-good.zip'


class TaskHelper(object):
    """
    I help with the creation of tasks
    """
    @staticmethod
    def download(url, out, overwrite=False, **kwargs):
        """
        Generate a task to download a file

        Note that, by default, downloads are never cleaned. You can
        change this behavior by sending clean=True along with the
        kwargs.

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
        from cpe_help.util.compression import extract_zipfile
        task = {
            'file_dep': [file],
            'targets': [dir],
            'actions': [(extract_zipfile, (file, dir))],
            'clean': [(maybe_rmtree, (dir,))],
        }
        task.update(kwargs)
        return task


def task_download_inputs():
    """
    Retrieve raw departments data from Kaggle
    """
    return {
        'actions': [
            'kaggle datasets download -d center-for-policing-equity/data-science-for-good -p data/inputs',
        ],
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
