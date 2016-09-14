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
