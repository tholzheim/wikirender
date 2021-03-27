'''
Created on 2021-03-27

@author: wf
'''
import unittest
from wikifile.smw import SMWPart

class TestSMWPart(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSMWPart(self):
        '''
        test SMW Parts
        '''
        smwParts=SMWPart.getAll(None)
        self.assertEqual(8,len(smwParts))
        self.assertEqual("list_of_page.jinja",smwParts["List of"].template)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()