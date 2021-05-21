'''
Created on 2021-04-06

@author: wf
'''
import unittest
import getpass
from wikifile.wikiFix import WikiFix


class TestWikiRender(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def inPublicCI(self):
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in ["travis", "runner"];

    def testWikiFix(self):
        if self.inPublicCI():
            pass
        fix = WikiFix('ormk')
        header, dicts = fix.getCsv(['3DUI 2020', '3DUI 2017'])
        self.assertIsNotNone(header)
        self.assertIsNotNone(dicts)
        self.assertEqual(len(dicts),2)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()