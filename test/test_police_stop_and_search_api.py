import unittest
import os
import shutil
import pandas as pd
from pandas.testing import assert_frame_equal

#from context import module_to_be_tested

'''
class TestFiles(unittest.TestCase):
    def test_files_infolder(self):
        """
        Test that it correctly picks up all files in folder,
        including sub folders. Does not return directories themselves.
        """
        folder = 'files_in_folder'
        expected = ['New Bitmap Image.bmp',
                    'New Microsoft Excel Worksheet.xlsx',
                    'New Text Document.txt',
                    'New folder\\New Bitmap Image.bmp']
        expected = list(map(lambda x: os.path.join(folder,x),expected))
        result = files_in_folder(folder)
        self.assertEqual(set(expected),set(result))
'''
