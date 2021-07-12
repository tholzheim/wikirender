import unittest
import warnings
import getpass
from wikifile.wikiFileManager import WikiFileManager
from wikibot.wikipush import WikiPush
from datetime import datetime
from random import random

class TestWikiFileManager(unittest.TestCase):
    '''
    test WikiFileManager
    '''

    def setUp(self):
        self.wikiId="wikirenderTest"
        self.fix = WikiFileManager(self.wikiId)
        self.pageTitle="Test_WikiFileManager"
        self.wikiSonName = "UnitTestPage"
        self.wikiPush = WikiPush(fromWikiId=self.wikiId, login=True)
        # filter annoying resource warnings
        testPageContent="""{{UnitTestPage
|name=Test page to test WikiFix
|randomValue=0.7220216381646549
|lastTested =2021-07-06 05:29:18.213316
}}
test freetext"""
        self.wikiPush.fromWiki.getPage(self.pageTitle).edit(testPageContent)
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

    def tearDown(self):
        pass

    def inPublicCI(self):
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in ["travis", "runner"];

    def testPagesListToDict(self):
        '''
        test converting a list of pages to a lookup dictionary by pageTitle
        '''
        
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
        act_res=self.fix.pagesListToDict(lod)
        self.assertTrue("Test Page 1" in act_res)
        self.assertTrue("label" in act_res["Test Page 1"])
        self.assertEqual(act_res, exp_res)

    def testGetWikiFile(self):
        if self.inPublicCI(): return
        wikiFile=self.fix.getWikiFile(self.pageTitle)
        wikiSon=wikiFile.extract_template(self.wikiSonName)
        self.assertTrue("name" in wikiSon)

    def testGetUpdatedPage(self):
        if self.inPublicCI(): return
        new_values={"label":"Test label", "year":"2020"}
        wikiFile=self.fix.getUpdatedPage(self.pageTitle, new_values, self.wikiSonName)
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
        # expected is something like this: [{'name': 'Test page to test WikiFix', 'randomValue': '0.10670651978101686', 'lastTested': '2021-06-01 22:55:53.787546', 'pageTitleTest': 'Test_WikiFileManager'}]
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
        # expected is something like this: [{'pageTitleTest': 'Test_WikiFileManager', 'lastTested': '2021-06-01 22:55:53.787546', 'Not existing property': None, 'name': 'Test page to test WikiFix', 'randomValue': '0.10670651978101686'}]
        self.assertTrue(len(lod)==1)
        record=lod[0]
        recordKeys=list(record.keys())
        for index, prop in enumerate(props):
            self.assertEqual(recordKeys[index], prop)
        self.assertTrue("name" in record)
        self.assertIsNone(record[propWithNoneValue])

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()