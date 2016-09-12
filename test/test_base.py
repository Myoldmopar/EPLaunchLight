import os
import sys

# add the source directory to the path so the unit test framework can find it
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'lib'))

import unittest

class TestSomethings(unittest.TestCase):

    def test_something(self):
		self.assertTrue(True)

# allow execution directly as python tests/test_ghx.py
if __name__ == '__main__':
	unittest.main()
