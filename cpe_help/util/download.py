import os
import subprocess

from cpe_help.util.path import ensure_path


def download(url, out):
    """
    Download a file from url to out

    If out already exists, it is replaced.

    Parameters
    ----------
    url : str
        The url to download from.
    out : str or Path
        The path to download to.

    Returns
    -------
    None
    """
    out = str(out)

    # delete file if it already exists
    try:
        os.remove(out)
    except FileNotFoundError:
        pass

    ensure_path(out)
    _download(url, out)


def _download(url, out):
    """
    Download a file, no checks
    """
    subprocess.run([
        'http',
        '--ignore-stdin',
        '--check-status',
        '--timeout=2.0',
        '--print=',
        '--download', url,
        '--output', out,
    ], check=True)
