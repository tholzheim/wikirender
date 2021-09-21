'''
Created on 2021-04-06

@author: wf
'''
import tempfile
import unittest
import getpass
from wikifile.wikiRender import WikiRender
from wikifile.metamodel import Topic

class TestWikiRender(unittest.TestCase):
    '''
    test wiki rendering
    '''
    topicJson = """{"data": [{"pageTitle": "Concept:Task", "name": "Task", "pluralName": "Tasks", "documentation": "Problem or issue that needs to be solved", "wikiDocumentation": "Problem or issue that needs to be solved"}]}
                """
    propJson = """{
            "data": [{
                "pageTitle": "Property:Task goals",
                "name": "Task goals",
                "label": "Goals",
                "type": null,
                "index": null,
                "sortPos": null,
                "primaryKey": "f",
                "mandatory": "f",
                "namespace": null,
                "size": null,
                "uploadable": "f",
                "defaultValue": null,
                "inputType": "textarea",
                "allowedValues": null,
                "documentation": "Goals that must be achieved to complete the task",
                "values_from": null,
                "showInGrid": "f",
                "isLink": "f",
                "nullable": "f",
                "topic": "Concept:Task",
                "regexp": null
                }, {
                "pageTitle": "Property:Task procedure",
                "name": "Task procedure",
                "label": "Procedure",
                "type": null,
                "index": null,
                "sortPos": null,
                "primaryKey": "f",
                "mandatory": "f",
                "namespace": null,
                "size": null,
                "uploadable": "f",
                "defaultValue": null,
                "inputType": "textarea",
                "allowedValues": null,
                "documentation": "Explanation or hints how the task should be solved.",
                "values_from": null,
                "showInGrid": "f",
                "isLink": "f",
                "nullable": "f",
                "topic": "Concept:Task",
                "regexp": null
                }, {
                "pageTitle": "Property:Task task",
                "name": "Task task",
                "label": "Task",
                "type": null,
                "index": null,
                "sortPos": null,
                "primaryKey": "f",
                "mandatory": "f",
                "namespace": null,
                "size": null,
                "uploadable": "f",
                "defaultValue": null,
                "inputType": "text",
                "allowedValues": null,
                "documentation": "Description of the task defining briefly the topic of the task.",
                "values_from": null,
                "showInGrid": "f",
                "isLink": "f",
                "nullable": "f",
                "topic": "Concept:Task",
                "regexp": null
                }, {
                "pageTitle": "Property:Task workpackage",
                "name": "Task workpackage",
                "label": "assigned to",
                "type": "Special:Types/Page",
                "index": null,
                "sortPos": null,
                "primaryKey": "f",
                "mandatory": "f",
                "namespace": null,
                "size": null,
                "uploadable": "f",
                "defaultValue": null,
                "inputType": null,
                "allowedValues": null,
                "documentation": "Workpackage the task is assigned to",
                "values_from": "concept=Workpackage",
                "showInGrid": "f",
                "isLink": "f",
                "nullable": "f",
                "topic": "Concept:Task",
                "regexp": null
                }]
            }"""


    def tearDown(self):
        pass

        
    def inPublicCI(self):
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in [ "travis", "runner" ];

    def testWikiRender(self):

        topic=Topic.from_wiki_json(self.topicJson, self.propJson)
        self.assertEqual(4, len(topic.properties))
        wikiRender=WikiRender(debug=True)
        with tempfile.TemporaryDirectory() as tempDir:
            wikiRender.generateTopic(topic, path=tempDir, overwrite=True)
            print("Wait")
        
        pass

    def test_render_metamodel(self):
        """
        test the rendering of the metamodel technical pages
        """
        #ToDo:
        # wikiRender = WikiRender(debug=True)
        # wikiRender.render_metamodel()
        pass

    def testRenderProperty(self):
        '''test rendering a property page'''
        topic = Topic.from_wiki_json(self.topicJson, self.propJson)
        prop=topic.properties[0]
        wikiRender=WikiRender()
        with tempfile.TemporaryDirectory() as tempDir:
            wikiRender.generateProperty(prop, path=tempDir, overwrite=True)
            with open(f"{tempDir}/{prop.get_pageTitle(withNamespace=True)}.wiki",  mode="r") as f:
                generatedPage=f.read()
                self.assertTrue(f"name={prop.name}" in generatedPage)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()