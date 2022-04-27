import os
import tempfile
from pathlib import Path
import sys
import unittest
import threading

# add the source directory to the path so the unit test framework can find it
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'EPLaunchLite'))

try:
    # noinspection PyUnresolvedReferences
    from EPLaunchLite.FileTypes import FileTypes  # IDE things FileTypes should be in the except block, but it shouldn't
    has_gtk = True
except ImportError as e:
    has_gtk = False
from EPLaunchLite.EnergyPlusThread import EnergyPlusThread


def make_eplus_executable(eplus_dir: Path):
    eplus_dir.mkdir()
    exe = eplus_dir / 'energyplus'
    exe.write_text("")


@unittest.skipIf(not has_gtk, "Cannot run FileTypes tests without gtk")
class TestFileTypes(unittest.TestCase):
    def test_idf_file_type(self):
        msg, filters = FileTypes.get_materials(FileTypes.IDF)
        self.assertEqual(len(filters), 2)  # should return 2: idf and imf
        # make sure we have each one, idf and imf
        idf_filters = [x for x in filters if 'IDF' in x.get_name()]
        self.assertTrue(len(idf_filters), 1)
        imf_filters = [x for x in filters if 'IMF' in x.get_name()]
        self.assertTrue(len(imf_filters), 1)

    def test_epw_file_type(self):
        msg, filters = FileTypes.get_materials(FileTypes.EPW)
        self.assertEqual(len(filters), 1)
        epw_filters = [x for x in filters if 'EPW' in x.get_name()]
        self.assertTrue(len(epw_filters), 1)

    def test_invalid_file_type(self):
        msg, result = FileTypes.get_materials('abcdef')
        self.assertIsNone(msg)
        self.assertIsNone(result)


class TestEnergyPlusThread(unittest.TestCase):
    def test_construction(self):
        paths = ['/dummy/', '/path', '/to_nothing']
        temp_dir = Path(tempfile.mkdtemp())
        eplus_dir = temp_dir / 'EnergyPlus-8-1-0'
        make_eplus_executable(eplus_dir)
        obj = EnergyPlusThread(eplus_dir / 'energyplus', Path(paths[1]), Path(paths[2]), None, None, None, None)
        self.assertTrue(isinstance(obj, threading.Thread))
        self.assertTrue(obj.run_script, paths[0])
        self.assertTrue(obj.input_file, paths[1])
        self.assertTrue(obj.weather_file, paths[2])


# allow execution directly as python tests/test_ghx.py
if __name__ == '__main__':
    unittest.main()
