import unittest
import warnings
import getpass
from pathlib import Path

from wikibot.wikiuser import WikiUser

from wikifile.wikiFileManager import WikiFileManager
from wikibot.wikipush import WikiPush
from datetime import datetime
from random import random
import io
import os
import time
from tests.default_wikiuser import DefaultWikiUser

class TestWikiFileManager(unittest.TestCase):
    '''
    test WikiFileManager
    '''

    @classmethod
    def setUpClass(cls):
        super(TestWikiFileManager, cls).setUpClass()
        cls.wikiFileManagers={}
        for wikiId in ["or","orclone","wikirenderTest"]:
            _wikiUser=DefaultWikiUser.getSMW_WikiUser(wikiId)
            home = os.path.expanduser("~")
            wikiTextPath=f"{home}/.or/wikibackup/{wikiId}"
            wikiFileManager=WikiFileManager(sourceWikiId=wikiId,wikiTextPath=wikiTextPath,login=False)
            cls.wikiFileManagers[wikiId]=wikiFileManager
        
    def setUp(self):
        self.sourcePath=f"{Path.home()}/.or/wikibackup/or"
        self.wikiId="wikirenderTest"
        self.wikiFileManager = WikiFileManager(self.wikiId, targetWikiId=self.wikiId)
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


    def testGetWikiAllWikiFilesForArgs(self):
        '''
        test getting wiki files for the args
        '''
        args = ["--pages", "3DUI", "3DUI 2020","3DUI 2016", "--source", "orclone","--template","Event"]
        wikiFileManager=TestWikiFileManager.wikiFileManagers["orclone"]
        wikiFileManager.getParser()
        args= wikiFileManager.parser.parse_args(args)
        wikiFiles = wikiFileManager.getAllWikiFilesForArgs(args)
        self.assertEqual(2,len(wikiFiles))

    def testGetWikiClient(self):
        '''
        test getting my wikiclient
        '''
        wikiClient=self.wikiFileManager.getWikiClient()
        self.assertEqual(self.wikiId,wikiClient.wikiUser.wikiId)
        pass

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
        act_res=self.wikiFileManager.pagesListToDict(lod)
        self.assertTrue("Test Page 1" in act_res)
        self.assertTrue("label" in act_res["Test Page 1"])
        self.assertEqual(act_res, exp_res)

    def testGetWikiFile(self):
        '''
        get the wiki file for the pageTitle
        '''
        wikiFile=self.wikiFileManager.getWikiFile(self.pageTitle)
        wikiSon=wikiFile.extract_template(self.wikiSonName)
        self.assertTrue("name" in wikiSon)

    def testGetUpdatedPage(self):
        '''
        test updating a page
        '''
        new_values={"label":"Test label", "year":"2020"}
        wikiFile=self.wikiFileManager.getUpdatedPage(self.pageTitle, new_values, self.wikiSonName)
        wikiSon = wikiFile.extract_template(self.wikiSonName)
        self.assertTrue("label" in wikiSon)
        self.assertTrue("year" in wikiSon)

    def testGetUpdatedPages(self):
        '''
        test updating multiple pages
        '''
        records={self.pageTitle:{"label":"Test label", "year":"2020"}}
        wikiFiles=self.wikiFileManager.getUpdatedPages(records, self.wikiSonName)
        self.assertTrue(len(wikiFiles)==1)
        wikiSon = wikiFiles[0].extract_template(self.wikiSonName)
        self.assertTrue("name" in wikiSon)
        self.assertTrue("label" in wikiSon)

    def testPushWikiFilesToWiki(self):
        '''
        test pushing files to the wiki
        '''
        timestampOfTest=datetime.now()
        new_values={"lastTested":str(timestampOfTest)}
        wikiFile=self.wikiFileManager.getUpdatedPage(self.pageTitle, new_values, self.wikiSonName)
        self.wikiFileManager.pushWikiFilesToWiki([wikiFile])
        pushed_wikiFile=self.wikiFileManager.getWikiFile(self.pageTitle)
        wikiSon=pushed_wikiFile.extract_template(self.wikiSonName)
        self.assertTrue("lastTested" in wikiSon)
        self.assertEqual(wikiSon["lastTested"], str(timestampOfTest))

    def testImportLODtoWiki(self):
        '''
        test importing a list of dicts to the wiki
        '''
        random_val=random()
        data=[{"pageTitle":self.pageTitle,"randomValue": str(random_val)}]
        self.wikiFileManager.importLODtoWiki(data, self.wikiSonName)
        # Test if import was executed correctly
        pushed_wikiFile = self.wikiFileManager.getWikiFile(self.pageTitle)
        wikiSon = pushed_wikiFile.extract_template(self.wikiSonName)
        self.assertTrue("randomValue" in wikiSon)
        self.assertEqual(wikiSon["randomValue"], str(random_val))

    def testExportWikiSonToLOD(self):
        '''
        test exporting the Markup in WikiSon to a list of dicts
        '''
        pageTitleKey="pageTitleTest"
        lod=self.wikiFileManager.exportWikiSonToLOD([self.pageTitle], self.wikiSonName, pageTitleKey)
        # expected is something like this: [{'name': 'Test page to test WikiFix', 'randomValue': '0.10670651978101686', 'lastTested': '2021-06-01 22:55:53.787546', 'pageTitleTest': 'Test_WikiFileManager'}]
        self.assertTrue(len(lod)==1)
        self.assertTrue("name" in lod[0])
        self.assertTrue(pageTitleKey in lod[0])

        # Extended Test
        propWithNoneValue="Not existing property"
        props=[pageTitleKey, "lastTested", propWithNoneValue]
        lod=self.wikiFileManager.exportWikiSonToLOD([self.pageTitle],
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

    def testGetAllPageTitlesFromFile(self):
        '''
        test utility function to get pageTitles from a file e.g. stdin
        '''
        # we'd love to test form a string
        # see https://stackoverflow.com/a/141451/1497139
        pageTitles="""Concept:Topic
Help:Topic"""
        fstdin = io.StringIO(pageTitles)
        pageTitleList=self.wikiFileManager.getAllPageTitlesFromFile(fstdin)
        debug=True
        if debug:
            print(pageTitleList)
        self.assertEqual(2,len(pageTitleList))
        
    def testGetAllWikiFiles(self):
        '''
        test getting all pages for the given backups
        '''
        for wikiId in ["or","orclone"]:
            wikiFileManager=TestWikiFileManager.wikiFileManagers[wikiId]
            wikiFiles=wikiFileManager.getAllWikiFiles()
            if self.debug:
                print(f"There are {len(wikiFiles)} wikiFiles for {wikiId}")
            self.assertTrue(len(wikiFiles)>18500)

    def test_getPageTitlesLocatedAt(self):
        '''
        test if the pageTitles of all wikiText files located in a directory are recognized as pages
        '''
        pageTitles=self.wikiFileManager.getPageTitlesLocatedAt(self.sourcePath)
        self.assertTrue(len(pageTitles)>1000)
        
    def testConvertWikiFilesToLOD(self):
        '''
        test the conversion to List of Dicts
        
        takes some 18 secs in total on 2,3 GHz 8-Core Intel Core i9
        '''
        profile=True
        for wikiId in ["or","orclone"]:
            if profile:
                print(f"Starting conversion form WikiFile to LoD for {wikiId} ...")
            wikiFileManager=TestWikiFileManager.wikiFileManagers[wikiId]
            templateName="Event"
            startTime=time.time()
            eventWikiFiles=wikiFileManager.getWikiFilesForTemplate(templateName)
            elapsed=time.time()-startTime
            if profile:
                print(f"getting  {len(eventWikiFiles)} wikiFiles for {wikiId} took {elapsed:5.1f} s")
            startTime=time.time()
            lod=wikiFileManager.convertWikiFilesToLOD(eventWikiFiles.values(),templateName)
            elapsed=time.time()-startTime
            if profile:
                print(f"converting {len(eventWikiFiles)} to List of Dicts for {wikiId} took {elapsed:5.1f} s")
            self.assertEqual(len(lod),len(eventWikiFiles))

    def testConvertWikiFilesToLODTemplateMissing(self):
        '''
        tests the convertWikiFilesToLOD behavior if a wikifile does not contain the requested template
        see https://github.com/tholzheim/wikirender/issues/16
        '''
        for wikiId in ["or", "orclone"]:
            wikiFileManager = TestWikiFileManager.wikiFileManagers[wikiId]
            templateName = "Event"
            wikiFiles=[wikiFileManager.getWikiFile("3DUI")]
            lod = wikiFileManager.convertWikiFilesToLOD(wikiFiles, templateName)
            self.assertTrue(lod==[])

    def testWikiUser(self):
        wikiUser=self.wikiFileManager.wikiUser
        self.assertTrue(isinstance(wikiUser, WikiUser))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()