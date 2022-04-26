from typing import List
from pathlib import Path
from platform import system


class SingleEnergyPlusPath:
    def __init__(self, dir_path: Path):
        self.eplus_root = dir_path
        self.eplus_executable = self.get_eplus_executable()

    def get_eplus_executable(self) -> Path:
        for ep_filename in ['energyplus', 'EnergyPlus']:
            if (self.eplus_root / ep_filename).exists():
                return self.eplus_root / ep_filename
        raise Exception(f"Could not detect EnergyPlus executable in {self.eplus_root}")

    def get_version_number(self):
        if 'EnergyPlus' not in self.eplus_root.name:
            return None
        return self.eplus_root.name[11:]


class EnergyPlusPathManager:
    def __init__(self, install_root_folder: Path = None):
        self.all_found_eplus_dirs: List[Path] = []
        self.install_root_folder = install_root_folder
        if self.install_root_folder is None:
            self.install_root_folder = EnergyPlusPathManager.platform_install_root()

    @staticmethod
    def platform_install_root() -> Path:
        if system() == 'Linux':
            return Path('/usr/local/bin')
        else:
            return Path('Applications')

    def get_latest_eplus_version(self) -> SingleEnergyPlusPath:
        install_folders = self.install_root_folder.glob('EnergyPlus*')
        ep_folders = []
        for i in install_folders:
            # noinspection PyBroadException
            try:
                if 'EnergyPlus' in i.name:
                    e_path = SingleEnergyPlusPath(i)
                    ep_folders.append(e_path)
            except Exception:
                pass  # just skip this folder, its fine, just not an E+ folder
        ep_versions = sorted(ep_folders, key=lambda x: x.get_version_number())
        if len(ep_versions) < 1:
            raise Exception("Could not find an E+ install root, try passing E+ install as command line argument")
        return ep_versions[-1]
