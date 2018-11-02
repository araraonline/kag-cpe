import configparser

from cpe_help.util.path import CONFIG_PATH


def get_configuration():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config


def get_acs_variables():
    result = []
    config = get_configuration()
    default_keys = list(config['DEFAULT'])
    for key in config['ACS Variables'].keys():
        if key not in default_keys:
            result.append(key)
    result = [x.upper() for x in result]
    return result
