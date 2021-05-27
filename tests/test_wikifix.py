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

    def testExportCsvContent(self):
        if self.inPublicCI(): return
        fix= WikiFix('ormk',debug=True)
        pageTitles=fix.getEventsinSeries('3DUI','Event in series')
        header, dicts = fix.getCsv(pageTitles)
        fix.exportToCsv(header,dicts)
        LOD= fix.prepareExportCsvContent('dict.csv')
        self.assertIsNotNone(LOD)
        failures= fix.exportCsvToWiki(LOD)
        self.assertEqual(len(failures),0)

    def testEventsinSeries(self):
        if self.inPublicCI(): return
        fix = WikiFix('ormk')
        events=fix.getEventsinSeries('3DUI','Event in series')
        self.assertTrue('3DUI 2017' in events)

    def testEditProperty(self):
        if self.inPublicCI(): return
        sampleDict= {'Acronym':'test'}
        fix = WikiFix('ormk')
        fixedDict=fix.editProperty(sampleDict,'Acronym','testpassed')
        self.assertIsNotNone(fixedDict)
        self.assertEqual(fixedDict['Acronym'],'testpassed')
        fixedDict2 = fix.editProperty(sampleDict, 'NewProperty', 'testpassed')
        self.assertIsNotNone(fixedDict2)
        self.assertEqual(fixedDict2['NewProperty'], 'testpassed')

    def testWikiFix(self):
        if self.inPublicCI(): return
        fix = WikiFix('ormk')
        header, dicts = fix.getCsv(['3DUI 2020', '3DUI 2017'])
        self.assertIsNotNone(header)
        self.assertIsNotNone(dicts)
        self.assertEqual(len(dicts),2)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()