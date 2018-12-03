# make submodules accessible like
# >>> from cpe_help import util
# >>> util.io.load_shp
# <function cpe_help.util.io.load_shp(path)>
__all__ = [
    'compression',
    'configuration',
    'crs',
    'download',
    'files',
    'interpolation',
    'io',
    'misc',
    'path',
    'testing',
]

from cpe_help.util.doit_tasks import TaskHelper
from cpe_help.util.configuration import get_configuration
