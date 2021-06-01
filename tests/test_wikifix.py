import unittest
import getpass
from datetime import datetime
from random import random

import pkg_resources

from wikifile.wikiFix import WikiFix

class TestWikiFix(unittest.TestCase):

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

    def testPagesListtoDict(self):
        if self.inPublicCI(): return
        fix = WikiFix('ormk')
        lod=[
            {
                "pageTitle":"Test Page 1",
                "label":"Test"
            },
            {
                "pageTitle": "Test Page 2",
                "label": "Test",
                "year":"2020"
            }
        ]
        exp_res={
            "Test Page 1":{
                "label":"Test"
            },
            "Test Page 2": {
                "label": "Test",
                "year": "2020"
            }
        }
        act_res=fix.pagesListtoDict(lod)
        self.assertTrue("Test Page 1" in act_res)
        self.assertTrue("label" in act_res["Test Page 1"])
        self.assertEqual(act_res, exp_res)

    def testGetWikiFile(self):
        if self.inPublicCI(): return
        fix = WikiFix('orth')
        wikiSonName = "UnitTestPage"
        wikiFile=fix.getWikiFile("Test_WikiFix")
        wikiSon=wikiFile.extract_template(wikiSonName)
        self.assertTrue("name" in wikiSon)

    def testGetUpdatedPage(self):
        if self.inPublicCI(): return
        fix = WikiFix('orth')
        new_values={"label":"Test label", "year":"2020"}
        wikiSonName="UnitTestPage"
        wikiFile=fix.getUpdatedPage("Test_WikiFix", new_values, wikiSonName)
        wikiSon = wikiFile.extract_template(wikiSonName)
        self.assertTrue("label" in wikiSon)
        self.assertTrue("year" in wikiSon)

    def testGetUpdatedPages(self):
        if self.inPublicCI(): return
        fix = WikiFix('orth')
        records={"Test_WikiFix":{"label":"Test label", "year":"2020"}}
        wikiSonName = "UnitTestPage"
        wikiFiles=fix.getUpdatedPages(records, wikiSonName)
        self.assertTrue(len(wikiFiles)==1)
        wikiSon = wikiFiles[0].extract_template(wikiSonName)
        self.assertTrue("name" in wikiSon)
        self.assertTrue("label" in wikiSon)

    def testPushWikiFilesToWiki(self):
        if self.inPublicCI(): return
        fix = WikiFix('orth')
        pageTitle="Test_WikiFix2"
        wikiSonName = "UnitTestPage"
        timestampOfTest=datetime.now()
        new_values={"lastTested":str(timestampOfTest)}
        wikiFile=fix.getUpdatedPage(pageTitle, new_values, wikiSonName)
        fix.pushWikiFilesToWiki([wikiFile])
        pushed_wikiFile=fix.getWikiFile(pageTitle)
        wikiSon=pushed_wikiFile.extract_template(wikiSonName)
        self.assertTrue("lastTested" in wikiSon)
        self.assertEqual(wikiSon["lastTested"], str(timestampOfTest))

    def testImportLODtoWiki(self):
        if self.inPublicCI(): return
        fix = WikiFix('orth')
        pageTitle="Test_WikiFix"
        wikiSonName = "UnitTestPage"
        random_val=random()
        data=[{"pageTitle":pageTitle,"randomValue": str(random_val)}]
        fix.importLODtoWiki(data, wikiSonName)
        # Test if import was executed correctly
        pushed_wikiFile = fix.getWikiFile(pageTitle)
        wikiSon = pushed_wikiFile.extract_template(wikiSonName)
        self.assertTrue("randomValue" in wikiSon)
        self.assertEqual(wikiSon["randomValue"], str(random_val))

    def testConvertCSVtoLOD(self):
        if self.inPublicCI(): return
        fix = WikiFix('orth')
        csv_raw="""pageTitle,name,label
page_1,Test Page 1, 1
page_2,Test Page 2, 2"""
        lod=fix.convertCSVtoLOD(csv_raw)
        self.assertTrue(len(lod) == 2)
        self.assertTrue("name" in lod[0])
        self.assertTrue(len(lod[0])==3)
        self.assertEqual("Test Page 1", lod[0]["name"])


    def  testGetFile(self):
        if self.inPublicCI(): return
        fix = WikiFix('orth')
        test_csv=pkg_resources.resource_filename('tests','resources/import_test.csv')
        exp_content="""pageTitle, lastTested
Test_WikiFix, 2021"""
        actual_content=fix.readFile(test_csv)
        self.assertEqual(actual_content,exp_content)

    def testImportCSVContentToWiki(self):
        if self.inPublicCI(): return
        fix = WikiFix('orth')
        pageTitle="Test_WikiFix"
        wikiSonName = "UnitTestPage"
        timestampOfTest = self.getTimestamp()
        csv_content = """pageTitle,lastTested
%s,%s""" % (pageTitle,timestampOfTest)
        fix.importCSVContentToWiki(csv_content, wikiSonName)
        pushed_wikiFile = fix.getWikiFile(pageTitle=pageTitle)
        wikiSon = pushed_wikiFile.extract_template(wikiSonName)
        self.assertTrue("lastTested" in wikiSon)
        self.assertEqual(wikiSon["lastTested"], timestampOfTest)


    def getTimestamp(self)->str:
        timestampOfTest = datetime.now()
        return str(timestampOfTest)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()