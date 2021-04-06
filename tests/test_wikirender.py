'''
Created on 2021-04-06

@author: wf
'''
import unittest
import getpass
from wikifile.wikiRender import WikiRender
from wikifile.metamodel import Topic

class TestWikiRender(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

        
    def inPublicCI(self):
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in [ "travis", "runner" ];

    def testWikiRender(self):
        if self.inPublicCI():
            return
        topicJson="""{"data": [{"pageName": "Concept:Task", "name": "Task", "pluralName": "Tasks", "documentation": "Problem or issue that needs to be solved", "wikiDocumentation": "Problem or issue that needs to be solved"}]}
        """
        propJson="""{
  "data": [{
    "pageName": "Property:Task goals",
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
    "pageName": "Property:Task procedure",
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
    "pageName": "Property:Task task",
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
    "pageName": "Property:Task workpackage",
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
        topic=Topic.fromWikiJson(topicJson,propJson)
        self.assertEqual(4,len(topic.properties))
        wikiRender=WikiRender()
        wikiRender.generateTopic(topic)
        
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()