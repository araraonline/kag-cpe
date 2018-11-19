"""
Tools for dealing with file compression
"""

import pathlib
import shutil

from cpe_help.util.files import (
    maybe_rmfile,
    maybe_rmtree,
)


def make_zipfile(filename, root_dir):
    """
    Create a zip archive with the contents of root_dir

    If filename is points to an existing file, it will first be removed.

    Parameters
    ----------
    filename : str or pathlib.Path
        The name of the file to create (e.g. 'foo.zip').
    root_dir : str or pathlib.Path
        The directory to retrieve contents from.

    Returns
    -------
    None
    """
    path = pathlib.Path(filename)
    maybe_rmfile(path)
    shutil.make_archive(path.with_suffix(''), 'zip', root_dir)


def extract_zipfile(filename, extract_dir):
    """
    Extract contents from a ZIP archive into extract_dir

    If extract_dir already exists, it is totally removed before
    extraction.

    Parameters
    ----------
    filename : str or pathlib.Path
        The input ZIP file.
    extract_dir : str or pathlib.Path
        The directory to extract the ZIP contents to.

    Returns
    -------
    None
    """
    maybe_rmtree(extract_dir)
    shutil.unpack_archive(filename, extract_dir, 'zip')
