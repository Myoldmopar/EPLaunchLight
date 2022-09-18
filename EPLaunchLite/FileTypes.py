from typing import List, Tuple, Union


class FileTypes(object):
    IDF = 1
    EPW = 2

    @staticmethod
    def get_materials(file_type) -> Tuple[Union[None, str], Union[None, List[Tuple[str, str]]]]:
        filters = []
        if file_type == FileTypes.IDF:
            message = "Select input file"
            idf_filter = ("IDF files", "*.idf")
            filters.append(idf_filter)
            imf_filter = ("IMF files", "*.imf")
            filters.append(imf_filter)
        elif file_type == FileTypes.EPW:
            message = "Select weather file"
            epw_filter = ("EPW files", "*.epw")
            filters.append(epw_filter)
        else:
            return None, None
        return message, filters
