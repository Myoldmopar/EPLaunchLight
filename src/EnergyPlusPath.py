import glob


class EnergyPlusPath(object):
    @staticmethod
    def get_version_number_from_path(path):
        ep_folder = path.split('/')[2]
        if 'EnergyPlus' not in ep_folder:
            return None
        return ep_folder[11:]

    @staticmethod
    def get_path_from_version_number(version):
        return '/Applications/EnergyPlus-%s' % version

    @staticmethod
    def get_latest_eplus_version():
        # get all the installed versions first, sorted
        install_folders = glob.glob('/Applications/EnergyPlus*')

        # then process them into a nice list
        ep_versions = sorted([EnergyPlusPath.get_version_number_from_path(x) for x in install_folders])

        # set current_entry to something meaningful if needed
        new_version = ep_versions[-1]
        return EnergyPlusPath.get_path_from_version_number(new_version)
