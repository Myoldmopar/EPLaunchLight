class FileTypes:
    IDF = 1
    EPW = 2

    @staticmethod
    def get_materials(file_type):
        if file_type == FileTypes.IDF:
            message = "Select input file"
            pattern_message = "IDF files"
            pattern = "*.idf"
        elif file_type == FileTypes.EPW:
            message = "Select weather file"
            pattern_message = "EPW files"
            pattern = "*.epw"
        else:
            return None
        return message, pattern_message, pattern


class EnergyPlusPath:
    @staticmethod
    def get_version_number_from_path(path):
        ep_folder = path.split('/')[2]
        if not 'EnergyPlus' in ep_folder:
            return None
        return ep_folder[11:]

    @staticmethod
    def get_path_from_version_number(version):
        return '/Applications/EnergyPlus-%s' % version
