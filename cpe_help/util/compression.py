"""
Tools for dealing with file compression
"""

import subprocess
from pathlib import Path

from cpe_help.util.path import ensure_path, maybe_rmfile, maybe_rmtree


def make_zipfile(path, root_dir):
    """
    Create a zip archive with the contents of root_dir

    If path already exists, it will first be removed.

    Parameters
    ----------
    path : str or Path
        The output ZIP archive.
    root_dir : str or Path
        The directory to copy contens from.

    Returns
    -------
    None
    """
    from shutil import make_archive

    path = Path(path)
    maybe_rmfile(path)
    ensure_path(path)
    make_archive(path.with_suffix(''), 'zip', root_dir)


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
