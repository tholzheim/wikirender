import unittest
import getpass
from tabulate import tabulate
from wikifile.utils import Itemize, Link, Widget, Enumerate, MagicWord, Table, SubObject, TemplateParam, SetProperties, \
    SwitchFunction
from wikifile.wikiRender import WikiRender

class TestUtilsTemplate(unittest.TestCase):
    """
    Test the jinja template utils
    """

    def inPublicCI(self):
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in [ "travis", "runner" ];

    def setUp(self):
        self.debug = False
        self.templateEnv = WikiRender.getTemplateEnv()

    def tearDown(self):
        pass

    def test_render_entity(self):
        name = "Event"
        properties = { 'Title': 'SMWCon', 'Year': '2020', 'Description': "test value test value\n with line break"}
        template2 = self.templateEnv.from_string(
            "{% from 'macros/utils.jinja' import render_entity %}{{render_entity(name, properties)}}")
        outputText = template2.render(name=name, properties=properties)
        expected = """{{Event
|Title=SMWCon
|Year=2020
|Description=test value test value
 with line break
}}"""
        self.assertEqual(outputText, expected, "SMW entity was not rendered correctly.")

class TestUtils(unittest.TestCase):
    """
    Tests the util classes
    """

    def _testList(self, listType:Widget, listsChar:str):
        """
        tests rendering of lists
        """
        # test simple list
        records=["First", "Second", "Third"]
        expectedMarkup=f"{listsChar}First\n{listsChar}Second\n{listsChar}Third\n"
        self.assertEqual(expectedMarkup, str(listType(records)))
        # list with sublist
        records = ["First",["Sub-first", "Sub-second"], "Second", "Third",["Sub-first", "Sub-second"]]
        expectedMarkup = f"{listsChar}First\n{listsChar*2}Sub-first\n{listsChar*2}Sub-second\n{listsChar}Second\n{listsChar}Third\n{listsChar*2}Sub-first\n{listsChar*2}Sub-second\n"
        self.assertEqual(expectedMarkup, str(listType(records)))

    def testItemize(self):
        """
        tests rendering of unordered lists
        """
        self._testList(Itemize, "*")

    def testEnumerate(self):
        """
        tests rendering of ordered lists
        """
        self._testList(Enumerate, "#")

    def testLink(self):
        """
        test rendering of external links
        """
        url="https://mediawiki.org"
        text="mediawiki"
        expectedMarkup="[https://mediawiki.org mediawiki]"
        actualMarkup=Link(url,text).render()
        self.assertEqual(expectedMarkup, actualMarkup)

    def testMagicWord(self):
        expectedMarkup="{{PAGENAME}}"
        actualMarkup=str(MagicWord("PAGENAME"))
        self.assertEqual(expectedMarkup, actualMarkup)
        self.assertEqual(expectedMarkup, str(MagicWord.PAGENAME))

    def testWidgetPipelining(self):
        """
        tests the pipelining capability of the Widget classes
        """
        lod=[
            {
                "url":"https://mediawiki.org",
                "label":"mediawiki"
            },
            {
                "url": "//en.wikipedia.org",
                       "label": "wikipedia"
            },
            {
                "url": "mailto:info@example.org",
                       "label": "email me"
            }
        ]
        expectedMarkup="*[https://mediawiki.org mediawiki]\n*[//en.wikipedia.org wikipedia]\n*[mailto:info@example.org email me]\n"
        markupList=str(Itemize([Link(record['url'], record['label']) for record in lod]))
        self.assertEqual(expectedMarkup, markupList)

    def testTable(self):
        """
        tests rendering of tables in mediawiki markup
        """
        lod=[{1:"Orange", 2:"Apple", 3:"more"},
             {1:"Bread",2:"Pie",3:"more"},
             {1:"Butter",2:"Ice<br/>cream",3:"and<br/>more"}]
        expectedMarkup="""{| class="wikitable" style="text-align: left;"
|+ <!-- caption -->
|-
! 1      !! 2             !! 3
|-
| Orange || Apple         || more
|-
| Bread  || Pie           || more
|-
| Butter || Ice<br/>cream || and<br/>more
|}"""
        actualMarkup=str(Table(lod))
        self.assertEqual(expectedMarkup, actualMarkup)

        expectedMarkupEscaped="""{{{!}} class="wikitable" style="text-align: left;"
{{!}}+ <!-- caption -->
{{!}}-
! 1      !! 2             !! 3
{{!}}-
{{!}} Orange {{!}}{{!}} Apple         {{!}}{{!}} more
{{!}}-
{{!}} Bread  {{!}}{{!}} Pie           {{!}}{{!}} more
{{!}}-
{{!}} Butter {{!}}{{!}} Ice<br/>cream {{!}}{{!}} and<br/>more
{{!}}}"""
        actualMarkupEscaped=str(Table(lod, escapePipe=True))
        self.assertEqual(expectedMarkupEscaped, actualMarkupEscaped)

    def testWigetTabulateCompability(self):
        lod = [
            {
                "url": "https://mediawiki.org",
                "label": "mediawiki"
            },
            {
                "url": "//en.wikipedia.org",
                "label": "wikipedia"
            },
            {
                "url": "mailto:info@example.org",
                "label": "email me"
            }
        ]
        expectedMarkup="""{| class="wikitable" style="text-align: left;"
|+ <!-- caption -->
|-
| [https://mediawiki.org mediawiki]
|-
| [//en.wikipedia.org wikipedia]
|-
| [mailto:info@example.org email me]
|}"""
        records=[{"link":Link(record['url'], record['label'])} for record in lod]
        actualMarkup=tabulate(records, tablefmt="mediawiki")
        self.assertEqual(expectedMarkup, actualMarkup)

    def testSubObject(self):
        """
        tests the redering of subobjects
        """
        expectedMarkup="""{{#subobject:street address
|street number=10
|street name=Parks Road
|postcode=OX1 3QD
|city=Oxford
|country=UK
}}"""
        properties={"street number":10,
                    "street name":"Parks Road",
                    "postcode":"OX1 3QD",
                    "city":"Oxford",
                    "country":"UK"}
        subobject=SubObject("street address",**properties)
        actualMarkup=subobject.render()
        self.assertEqual(expectedMarkup, actualMarkup)

    def testSetProperties(self):
        """
        tests the rendering of set parser function for assigning property values
        """
        expectedMarkup="""{{#set:
|street number=10
|street name=Parks Road
|postcode=OX1 3QD
|city=Oxford
|country=UK
}}"""
        properties = {"street number": 10,
                      "street name": "Parks Road",
                      "postcode": "OX1 3QD",
                      "city": "Oxford",
                      "country": "UK"}
        actualMarkup=SetProperties(**properties).render()
        self.assertEqual(expectedMarkup, actualMarkup)

    def testTemplateParam(self):
        expectedMarkup="{{{firstname|}}}"
        actualMarkup=TemplateParam("firstname").render()
        self.assertEqual(expectedMarkup, actualMarkup)

    def testSwitchFunction(self):
        """
        tests the rendering of a switch parser function
        """
        cases={
            "First":"Hello",
            "Second":"World",
            "Empty":"",
            "Fallthrough":None,
            "#default":"End of switch statement"
        }
        expectedMarkup="""{{#switch:Test
|First=Hello
|Second=World
|Empty=
|Fallthrough
|#default=End of switch statement
}}"""
        actualMarkup=SwitchFunction("Test", **cases).render()
        self.assertEqual(expectedMarkup, actualMarkup)

if __name__ == "__main__":
    unittest.main()
