import os
import pathlib
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


def ensure_path(path):
    """
    Ensure that the directories that lead to a path exist

    Parameters
    ----------
    path : str or Path

    Examples
    --------
    Create directories A and B (if they don't exist):

    >>> ensure_path('./A/B/file.py')

    The path can also point to a directory. This line below will have
    the same effect as the one above:

    >>> ensure_path('./A/B/C')
    """
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)