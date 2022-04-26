import json
import os

from EPLaunchLite.International import Languages
from EPLaunchLite.EnergyPlusPath import EnergyPlusPathManager


class Keys:
    last_idf_folder = 'last_idf_folder'
    last_epw_folder = 'last_epw_folder'
    last_idf = 'last_idf'
    last_epw = 'last_epw'
    language = 'language'
    install_root = 'install_root'


def load_settings(settings_file_name):
    # noinspection PyBroadException
    try:
        settings = json.load(open(settings_file_name))
    except Exception:  # any exception can cause this
        settings = {}
    if Keys.last_idf_folder not in settings:
        settings[Keys.last_idf_folder] = os.path.expanduser("~")
    if Keys.last_epw_folder not in settings:
        settings[Keys.last_epw_folder] = os.path.expanduser("~")
    if Keys.last_idf not in settings:
        settings[Keys.last_idf] = '/path/to/idf'
    if Keys.last_epw not in settings:
        settings[Keys.last_epw] = '/path/to/epw'
    if Keys.language not in settings:
        settings[Keys.language] = Languages.English
    if Keys.install_root not in settings:
        settings[Keys.install_root] = EnergyPlusPathManager.platform_install_root()
    return settings


def save_settings(settings, settings_file_name):
    # noinspection PyBroadException
    try:
        json.dump(settings, open(settings_file_name, 'w'))
    except Exception:
        pass
