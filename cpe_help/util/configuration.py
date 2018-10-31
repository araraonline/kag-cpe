import configparser

from cpe_help.util.path import CONFIG_PATH


def get_configuration():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config
