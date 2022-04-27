from pathlib import Path
from platform import system


class EnergyPlusPathManager:
    def __init__(self, predefined_path_string: str):
        """
        Manages the E+ path for this tool.  If the path is valid, this class instance's .valid member will be True.
        If valid is True, then you should be able to rely on the .eplus_path member variable to be the path to the
        EnergyPlus install root, and .executable should be the path to the EnergyPlus binary file.
        """
        if predefined_path_string:
            self.set_user_specified_path(Path(predefined_path_string))
            return
        # if we didn't get a predefined string, try to find the E+ root based on the current file
        this_file_path = Path(__file__).resolve()
        all_folder_names = this_file_path.parts
        self.eplus_path = this_file_path
        self.valid = False
        self.executable = None
        for x in range(len(all_folder_names)):
            self.eplus_path = self.eplus_path.parent  # trim off last item, the first time through this trim a file off
            if 'EnergyPlus' in self.eplus_path.name:  # if the final item has 'EnergyPlus', we assume we're at the root
                self.validate_path()
                break
        else:
            # if we didn't find 'EnergyPlus', we don't appear to be in an E+ install, just give a dummy path
            self.eplus_path = EnergyPlusPathManager.platform_install_root() / 'EnergyPlus-X-Y-Z'

    def set_user_specified_path(self, user_path: Path = None):
        self.eplus_path = user_path
        self.validate_path()

    def validate_path(self):
        self.valid = False
        if not self.eplus_path.exists():
            return
        for ep_filename in ['energyplus', 'EnergyPlus']:
            if (self.eplus_path / ep_filename).exists():
                self.executable = self.eplus_path / ep_filename
                self.valid = True
                return

    @staticmethod
    def platform_install_root() -> Path:
        if system() == 'Linux':
            return Path('/usr/local/bin')
        else:
            return Path('Applications')
