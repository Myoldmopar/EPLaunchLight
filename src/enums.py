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
        return message, pattern_message, pattern
