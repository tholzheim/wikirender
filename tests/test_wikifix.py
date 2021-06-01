import unittest
import getpass
from datetime import datetime
from random import random

import pkg_resources

from wikifile.wikiFix import WikiFix

class TestWikiFix(unittest.TestCase):

    def setUp(self):
        self.fix = WikiFix('orth')
        self.pageTitle="Test_WikiFix"
        self.wikiSonName = "UnitTestPage"

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
        act_res=self.fix.pagesListtoDict(lod)
        self.assertTrue("Test Page 1" in act_res)
        self.assertTrue("label" in act_res["Test Page 1"])
        self.assertEqual(act_res, exp_res)

    def testGetWikiFile(self):
        if self.inPublicCI(): return
        wikiFile=self.fix.getWikiFile("Test_WikiFix")
        wikiSon=wikiFile.extract_template(self.wikiSonName)
        self.assertTrue("name" in wikiSon)

    def testGetUpdatedPage(self):
        if self.inPublicCI(): return
        new_values={"label":"Test label", "year":"2020"}
        wikiFile=self.fix.getUpdatedPage("Test_WikiFix", new_values, self.wikiSonName)
        wikiSon = wikiFile.extract_template(self.wikiSonName)
        self.assertTrue("label" in wikiSon)
        self.assertTrue("year" in wikiSon)

    def testGetUpdatedPages(self):
        if self.inPublicCI(): return
        records={self.pageTitle:{"label":"Test label", "year":"2020"}}
        wikiFiles=self.fix.getUpdatedPages(records, self.wikiSonName)
        self.assertTrue(len(wikiFiles)==1)
        wikiSon = wikiFiles[0].extract_template(self.wikiSonName)
        self.assertTrue("name" in wikiSon)
        self.assertTrue("label" in wikiSon)

    def testPushWikiFilesToWiki(self):
        if self.inPublicCI(): return
        timestampOfTest=datetime.now()
        new_values={"lastTested":str(timestampOfTest)}
        wikiFile=self.fix.getUpdatedPage(self.pageTitle, new_values, self.wikiSonName)
        self.fix.pushWikiFilesToWiki([wikiFile])
        pushed_wikiFile=self.fix.getWikiFile(self.pageTitle)
        wikiSon=pushed_wikiFile.extract_template(self.wikiSonName)
        self.assertTrue("lastTested" in wikiSon)
        self.assertEqual(wikiSon["lastTested"], str(timestampOfTest))

    def testImportLODtoWiki(self):
        if self.inPublicCI(): return
        random_val=random()
        data=[{"pageTitle":self.pageTitle,"randomValue": str(random_val)}]
        self.fix.importLODtoWiki(data, self.wikiSonName)
        # Test if import was executed correctly
        pushed_wikiFile = self.fix.getWikiFile(self.pageTitle)
        wikiSon = pushed_wikiFile.extract_template(self.wikiSonName)
        self.assertTrue("randomValue" in wikiSon)
        self.assertEqual(wikiSon["randomValue"], str(random_val))

    def testConvertCSVtoLOD(self):
        if self.inPublicCI(): return
        csv_raw="""pageTitle,name,label
page_1,Test Page 1, 1
page_2,Test Page 2, 2"""
        lod=self.fix.convertCSVtoLOD(csv_raw)
        self.assertTrue(len(lod) == 2)
        self.assertTrue("name" in lod[0])
        self.assertTrue(len(lod[0])==3)
        self.assertEqual("Test Page 1", lod[0]["name"])


    def  testGetFile(self):
        if self.inPublicCI(): return
        test_csv=pkg_resources.resource_filename('tests','resources/import_test.csv')
        exp_content="""pageTitle, lastTested
Test_WikiFix, 2021"""
        actual_content=self.fix.readFile(test_csv)
        self.assertEqual(actual_content,exp_content)

    def testImportCSVContentToWiki(self):
        if self.inPublicCI(): return
        timestampOfTest = self.getTimestamp()
        csv_content = """pageTitle,lastTested
%s,%s""" % (self.pageTitle,timestampOfTest)
        self.fix.importCSVContentToWiki(csv_content, self.wikiSonName)
        pushed_wikiFile = self.fix.getWikiFile(pageTitle=self.pageTitle)
        wikiSon = pushed_wikiFile.extract_template(self.wikiSonName)
        self.assertTrue("lastTested" in wikiSon)
        self.assertEqual(wikiSon["lastTested"], timestampOfTest)

    def testExportWikiSonToLOD(self):
        if self.inPublicCI(): return
        pageTitleKey="pageTitleTest"
        lod=self.fix.exportWikiSonToLOD([self.pageTitle], self.wikiSonName, pageTitleKey)
        # expected is something like this: [{'name': 'Test page to test WikiFix', 'randomValue': '0.10670651978101686', 'lastTested': '2021-06-01 22:55:53.787546', 'pageTitleTest': 'Test_WikiFix'}]
        self.assertTrue(len(lod)==1)
        self.assertTrue("name" in lod[0])
        self.assertTrue(pageTitleKey in lod[0])

        # Extended Test
        propWithNoneValue="Not existing property"
        props=[pageTitleKey, "lastTested", propWithNoneValue]
        lod=self.fix.exportWikiSonToLOD([self.pageTitle],
                                        self.wikiSonName,
                                        pageTitleKey,
                                        properties=props)
        # expected is something like this: [{'pageTitleTest': 'Test_WikiFix', 'lastTested': '2021-06-01 22:55:53.787546', 'Not existing property': None, 'name': 'Test page to test WikiFix', 'randomValue': '0.10670651978101686'}]
        self.assertTrue(len(lod)==1)
        record=lod[0]
        recordKeys=list(record.keys())
        for index, prop in enumerate(props):
            self.assertEqual(recordKeys[index], prop)
        self.assertTrue("name" in record)
        self.assertIsNone(record[propWithNoneValue])

    def testExportWikiSonToCSV(self):
        if self.inPublicCI(): return
        csvString = self.fix.exportWikiSonToCSV([self.pageTitle],
                                                self.wikiSonName,
                                                pageTitleKey=self.pageTitle,
                                                properties=[self.pageTitle, "name"],
                                                limitProperties=True)
        exp_csv="Test_WikiFix,name\r\nTest_WikiFix,Test page to test WikiFix\r\n"
        self.assertEqual(csvString, exp_csv)

    def getTimestamp(self)->str:
        timestampOfTest = datetime.now()
        return str(timestampOfTest)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()