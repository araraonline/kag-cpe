"""
Utilities for creating/removing files and directories
"""

import os
import shutil


def maybe_mkdir(path):
    """
    Create a directory, if it doesn't exist

    Parameters
    ----------
    path : str or pathlib.Path
    """
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def maybe_rmfile(path):
    """
    Remove a file, if it exsits

    Parameters
    ----------
    path : str or pathlib.Path
    """
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def maybe_rmtree(path):
    """
    Remove a directory tree, if it exists

    Parameters
    ----------
    path : str or pathlib.Path
    """
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass
