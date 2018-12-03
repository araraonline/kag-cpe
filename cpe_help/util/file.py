"""
Utilities for creating/removing files and directories
"""

import os
import pathlib
import shutil


def list_files(directory):
    """
    List all files under a directory tree
    """
    return [pathlib.Path(parent) / file
            for parent, _, files in os.walk(directory)
            for file in files]


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
