"""
Shortcut for the main directories in this package
"""

import pathlib


_CWD = pathlib.Path(__file__).resolve().parent
BASE_DIR = _CWD.parent.parent
DATA_DIR = BASE_DIR / 'data'
INPUT_DIR = DATA_DIR / 'input'
CONFIG_PATH = BASE_DIR / 'cpe_help.conf'
