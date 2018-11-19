import os
import shutil


# Utils

def maybe_mkdir(path):
    """
    Create a directory, if it doesn't exist

    Parameters
    ----------
    path : str or Path
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
    path : str or Path
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
    path : str or Path
    """
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass
