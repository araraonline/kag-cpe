"""
Tools for dealing with file compression
"""

import shutil
import subprocess
from pathlib import Path

from cpe_help.util.path import ensure_path, maybe_rmfile, maybe_rmtree


def make_zipfile(filename, root_dir):
    """
    Create a zip archive with the contents of root_dir

    If filename is points to an existing file, it will first be removed.

    Parameters
    ----------
    filename : str or Path
        The name of the file to create (e.g. 'foo.zip').
    root_dir : str or Path
        The directory to retrieve contents from.

    Returns
    -------
    None
    """
    path = Path(filename)
    maybe_rmfile(path)
    ensure_path(path)
    shutil.make_archive(path.with_suffix(''), 'zip', root_dir)


def unzip(file, dir):
    """
    Extract files from a ZIP archive into dir

    If dir already exists, it is totally removed before extraction.

    Parameters
    ----------
    file : str or Path
        The input ZIP file.
    dir : str or Path
        The directory to extract the ZIP contents to.

    Returns
    -------
    None
    """
    # remove dir tree if it exists
    maybe_rmtree(dir)

    ensure_path(dir)
    _unzip(file, dir)


def _unzip(file, dir):
    """
    Extract contents from a ZIP file, no checks
    """
    subprocess.run([
        'unzip',
        file,
        '-d',
        dir
    ], check=True)
