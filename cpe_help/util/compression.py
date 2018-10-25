"""
Tools for dealing with file compression
"""

import shutil
import subprocess

from cpe_help.util.path import ensure_path


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
    try:
        shutil.rmtree(dir)
    except FileNotFoundError:
        pass

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
