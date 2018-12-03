import configparser

from cpe_help import util


def get_configuration():
    config = configparser.RawConfigParser()
    config.read(util.path.CONFIG_PATH)
    return config


def get_acs_variables():
    """
    Return a dictionary mapping variable names to be queried into how
    these variables should be named locally.
    """
    config = get_configuration()
    default_keys = list(config['DEFAULT'])
    result = {k.upper(): v
              for k, v in config['ACS Variables'].items()
              if k not in default_keys}
    return result
