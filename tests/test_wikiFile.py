import unittest
from pathlib import Path
from unittest import TestCase

from wikitextparser import Template

from wikifile.wikiFile import WikiFile
from wikifile.wikiFileManager import WikiFileManager
from wikifile.wikiRender import WikiRender


class TestWikiFile(TestCase):
    """
    Test the jinja template utils
    """

    def setUp(self):
        self.debug=False
        self.sourcePath = f"{Path.home()}/wikibackup/or"
        self.wikiId = "wikirenderTest"
        self.wikiFileManager = WikiFileManager(self.wikiId, wikiTextPath=self.sourcePath)
        self.wikiRender=WikiRender()
        self.sampleWikiFile="""
{{Event
|Acronym=3DUI 2020
|Title=IEEE Symposium on 3D User Interfaces
|Series=3DUI
|Type=Symposium
|Start date=2020/03/22
|End date=2020/03/26
|Submission deadline=2019/09/03
|Homepage=http://ieeevr.org/2020/
|City=Atlanta
|Country=USA
}}
        """
        self.sampleWikiFile_duplicateTemplate="""
{{Event
|Acronym=3DUI 2020
|Title=IEEE Symposium on 3D User Interfaces
|Series=3DUI
|Type=Symposium
|Start date=2020/03/22
|End date=2020/03/26
}}
{{Event
|Submission deadline=2019/09/03
|Homepage=http://ieeevr.org/2020/
|City=Atlanta
|Country=USA
}}
        """

    def tearDown(self):
        pass

    def test_get_template(self):
        '''
        test the get_template function
        '''
        wikiFile = WikiFile("sampleFile", self.wikiFileManager, self.sampleWikiFile)
        eventTemplate = wikiFile.get_template("Event")
        self.assertTrue(isinstance(eventTemplate,Template))
        self.assertTrue(len(eventTemplate.arguments)==10)
        self.debug=True
        if self.debug:
            print(eventTemplate)

    def test_get_template_name(self):
        expName="Event"
        rawName=" Event \n"
        name=WikiFile.get_template_name(rawName)
        self.assertEqual(name, expName)

    def test_extract_template(self):
        wikiFile = WikiFile("sampleFile", self.wikiFileManager,self.sampleWikiFile)
        eventRecord=wikiFile.extract_template("Event")
        self.assertTrue('Acronym' in eventRecord)
        self.assertEqual(eventRecord['Acronym'], "3DUI 2020")
        self.assertTrue('Series' in eventRecord)
        self.assertEqual(eventRecord['Series'], "3DUI")
        self.assertTrue('Start date' in eventRecord)
        self.assertEqual(eventRecord['Start date'], "2020/03/22")
        self.assertTrue('Homepage' in eventRecord)
        self.assertEqual(eventRecord['Homepage'], "http://ieeevr.org/2020/")

    def testNameValue(self):
        '''
        test getting content from wikiText
        '''
        wikiText="""{{SomeEntity
|a=1
|b=a=c
|b
|a='
}}"""
        wikiFile=WikiFile("somePage.wiki",self.wikiFileManager,wikiText=wikiText)
        someEntityDict=wikiFile.extract_template("SomeEntity")
        print(someEntityDict)
       
        
    def test_str(self):
        wikiFile = WikiFile("sampleFile", self.wikiFileManager, self.sampleWikiFile)
        wikiText=str(wikiFile)
        self.assertEqual(self.sampleWikiFile, wikiText)

    def test_str_adding_arguments(self):
        '''Test with adding template arguments'''
        rawString="{{Event|Acronym=3DUI 2020}}"
        expString="{{Event|Acronym=3DUI 2020|Title=Test}}"
        wikiFile = WikiFile("sampleFile", self.wikiFileManager, rawString)
        wikiFile.update_template("Event",{"Title":"Test"})
        wikiText=str(wikiFile).strip()
        self.assertEqual(expString, wikiText)

    def test_str_adding_arguments_prettify(self):
        '''
        tests Issue https://github.com/tholzheim/wikirender/issues/7
        Adding new values to a template in prettify mode should place each value into a new line
        '''
        rawString = "{{Event\n|Acronym=3DUI 2020\n}}"
        expString = "{{Event\n|Acronym=3DUI 2020\n|Title=Test\n}}"
        wikiFile = WikiFile("sampleFile", self.wikiFileManager, rawString)
        wikiFile.update_template("Event", {"Title": "Test"}, prettify=True)
        wikiText = str(wikiFile).strip()
        self.assertEqual(expString, wikiText)

    def test_sanitizePageTitle(self):
        '''
        tests sanitization of page titles
        '''
        testLoD=[
            {
                "raw":"3DUI 2020",
                "expected":"3DUI 2020"
            },
            {
                "raw": "3DUI 2020.wiki",
                "expected": "3DUI 2020"
            },
            {
                "raw": f"{self.sourcePath}/3DUI 2020.wiki",
                "expected":"3DUI 2020"
        }
        ]
        for testRecord in testLoD:
            name=testRecord.get('raw')
            wikiFile=WikiFile(name, self.wikiFileManager)
            actual=wikiFile.getPageTitle()
            self.assertEqual(testRecord.get('expected'),actual)
            
    def testIssue13(self):
        '''
        test https://github.com/tholzheim/wikirender/issues/13
        '''
        wikiFile=WikiFile(name="Hello",wikiText="Hello world!")
        self.assertTrue(wikiFile is not None)
        self.assertTrue(wikiFile.wikiFileManager is None)

if __name__ == "__main__":
    unittest.main()