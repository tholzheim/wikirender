import unittest
import getpass
from datetime import datetime
from random import random

import pkg_resources

from wikifile.wikiFileManager import WikiFileManager
import warnings

class TestWikiFileManager(unittest.TestCase):
    '''
    test WikiFileManager
    '''

    def setUp(self):
        if not self.inPublicCI():
            self.fix = WikiFileManager('orth')
            self.pageTitle="Test_WikiFix"
            self.wikiSonName = "UnitTestPage"
        # filter annoying resource warnings
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

    def tearDown(self):
        pass

    def inPublicCI(self):
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in ["travis", "runner"];

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

    def getTimestamp(self)->str:
        timestampOfTest = datetime.now()
        return str(timestampOfTest)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()