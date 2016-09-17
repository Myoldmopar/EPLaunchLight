import gtk


class FileTypes(object):
    IDF = 1
    EPW = 2

    @staticmethod
    def get_materials(file_type):
        filters = []
        if file_type == FileTypes.IDF:
            message = "Select input file"
            idf_filter = gtk.FileFilter()
            idf_filter.set_name("IDF files")
            idf_filter.add_pattern("*.idf")
            filters.append(idf_filter)
            imf_filter = gtk.FileFilter()
            imf_filter.set_name("IMF files")
            imf_filter.add_pattern("*.imf")
            filters.append(imf_filter)
        elif file_type == FileTypes.EPW:
            message = "Select weather file"
            epw_filter = gtk.FileFilter()
            epw_filter.set_name("EPW files")
            epw_filter.add_pattern("*.epw")
            filters.append(epw_filter)
        else:
            return None, None
        return message, filters
