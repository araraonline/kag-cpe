"""
Shortcut for the main directories in the project
"""

import pathlib


_CWD = pathlib.Path(__file__).resolve().parent
BASE_DIR = _CWD.parent.parent
DATA_DIR = BASE_DIR / 'data'
INPUT_DIR = DATA_DIR / 'input'
OUTPUT_DIR = DATA_DIR / 'output'
TEMPLATES_DIR = BASE_DIR / 'templates'
CONFIG_PATH = BASE_DIR / 'cpe_help.conf'
