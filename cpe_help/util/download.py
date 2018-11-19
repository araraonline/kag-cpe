import subprocess

from cpe_help.util.configuration import get_configuration
from cpe_help.util.files import maybe_rmfile


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
    maybe_rmfile(out)
    _download(url, out)


def _download(url, out):
    """
    Download a file, no checks

    Parameters
    ----------
    url : str
    out : str or Path
    """
    ua = get_configuration()['Downloads']['UserAgent']
    subprocess.run([
        'http',
        '--ignore-stdin',
        '--check-status',
        '--timeout=2.0',
        '--print=',
        '--output', str(out),
        '--download',
        url,
        'User-Agent:' + ua,
    ], check=True)
