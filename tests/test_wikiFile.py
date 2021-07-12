import unittest
from unittest import TestCase

from wikitextparser import Template

from wikifile.wikiFile import WikiFile
from wikifile.wikiRender import WikiRender


class TestWikiFile(TestCase):
    """
    Test the jinja template utils
    """

    def setUp(self):
        self.debug=False
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
<!-- PLEASE ADAPT OR DELETE THIS PART COMPLETELY - You can just paste in the call for papers and remove this and the last line

==Topics==
==Submissions==
==Important Dates==

==Committees==
* Co-Organizers
* General Co-Chairs
** [[has general chair::some person]], some affiliation, country

* PC Co-Chairs
** [[has program chair::some person]], some affiliation, country

* Workshop Chair
** [[has workshop chair::some person]], some affiliation, country

* Panel Chair
** [[has OC member::some person]], some affiliation, country

* Seminars Chair
** [[has tutorial chair::some person]], some affiliation, country

* Demonstration Co-Chairs
** [[has demo chair::some person]], some affiliation, country
** [[has demo chair::some person]], some affiliation, country

* Local Organizing Co-Chairs
** [[has local chair::some person]], some affiliation, country

* Program Committee Members
** [[has PC member::some person]], some affiliation, country
-->
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
        wikiFile = WikiFile("sampleFile", "tmp", self.wikiRender, self.sampleWikiFile)
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
        wikiFile = WikiFile("sampleFile", "tmp", self.wikiRender,self.sampleWikiFile)
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
        wikiFile=WikiFile("somePage.wiki","/tmp",wikiText=wikiText)
        someEntityDict=wikiFile.extract_template("SomeEntity")
        print(someEntityDict)
       
        
    def test_str(self):
        wikiFile = WikiFile("sampleFile", "tmp", self.wikiRender, self.sampleWikiFile)
        wikiText=str(wikiFile)
        self.assertEqual(self.sampleWikiFile, wikiText)

    def test_str_adding_arguments(self):
        '''Test with adding template arguments'''
        rawString="{{Event|Acronym=3DUI 2020}}"
        expString="{{Event|Acronym=3DUI 2020|Title=Test}}"
        wikiFile = WikiFile("sampleFile", "tmp", self.wikiRender, rawString)
        wikiFile.update_template("Event",{"Title":"Test"})
        wikiText=str(wikiFile).strip()
        self.assertEqual(expString, wikiText)

    def test_str_adding_arguments_pretttify(self):
        '''
        tests Issue https://github.com/tholzheim/wikirender/issues/7
        Adding new values to a template in prettify mode should place each value into a new line
        '''
        rawString = "{{Event\n|Acronym=3DUI 2020\n}}"
        expString = "{{Event\n|Acronym=3DUI 2020\n|Title=Test\n}}"
        wikiFile = WikiFile("sampleFile", "tmp", self.wikiRender, rawString)
        wikiFile.update_template("Event", {"Title": "Test"}, prettify=True)
        wikiText = str(wikiFile).strip()
        self.assertEqual(expString, wikiText)

if __name__ == "__main__":
    unittest.main()