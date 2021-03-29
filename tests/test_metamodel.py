'''
Created on 2021-03-27

@author: wf
'''
import unittest
from wikifile.metamodel import Context, Topic, Property, UML


class TestMetaModel(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testMetaModel(self):
        '''
        test the meta model
        '''
        context=Context({"name":"MetaModel"})
        self.assertEqual("MetaModel",context.name)
        topic=None
        #try:
        #    topic=Topic({"name":"Context","label":"Context"})
        #    self.fail("there should be an exception")
        #except Exception as ex:
        #    self.assertTrue("Invalid property 'label'" in str(ex))
        self.assertIsNone(topic)
        topic=Topic({"name":"Context","pluralName":"Contexts"})    
        self.assertEqual("Context",topic.name)
        self.assertEqual("Contexts",topic.plural_name)
        prop=Property({"name":"name","label":"name"})
        self.assertEqual("name",prop.name)
        self.assertEqual("name",prop.label)
        self.assertIsNone(prop.type)
        pass
    
    def testTopicFromJson(self):
        '''
        test loading/constructing from Json
        '''
        jsonStr="""{
  "data": [{
    "Topic": "Concept:Commit",
    "name": "Commit",
    "pluralName": "Commits",
    "documentation": "A Git commit",
    "wikiDocumentation": "see https://git-scm.com/docs/git-commit"
  },{
    "Topic": "Concept:Task",
    "name": "Task",
    "pluralName": "Tasks",
    "documentation": "Problem or issue that needs to be solved",
    "wikiDocumentation": "Problem or issue that needs to be solved"
  }]
}"""
        
        topics=Topic.fromJson(jsonStr)
        self.assertEqual(2,len(topics))
        commitTopic=topics[0]
        self.assertEqual("Commits",commitTopic.plural_name)
        taskTopic=topics[1]
        self.assertEqual("Task",taskTopic.name)
        
        
    def testPropertyFromJson(self):
        '''
        test loading/constructing from Json
        '''
        jsonStr="""{
        "data": [
{
    "": "Property:Task goals",
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
    "": "Property:Task procedure",
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
    "": "Property:Task task",
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
    "": "Property:Task workpackage",
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
    "documentation": "Worckpackage the task is assigned to",
    "values_from": "concept=Workpackage",
    "showInGrid": "f",
    "isLink": "f",
    "nullable": "f",
    "topic": "Concept:Task",
    "regexp": null
  }]
}"""
        props=Property.fromJson(jsonStr)
        self.assertEqual(4,len(props))
        wprop=props[3]
        self.assertEqual("assigned to",wprop.label)
        # TODO: wait for Type handling !!!
        #self.assertFalse(wprop.show_in_grid)
        self.assertTrue("f" in wprop.show_in_grid)

    def testUMLOutgoingEdges(self):
        data = {
                "Property": "Property:Task goals",
                "name": "Task goals",
                "label": "Goals",
                "type": "Special:Types/Page",
                "index": None,
                "sortPos": None,
                "primaryKey": False,
                "mandatory": False,
                "namespace": None,
                "size": None,
                "uploadable": False,
                "defaultValue": None,
                "inputType": "tokens",
                "allowedValues": None,
                "documentation": "Goals that must be achieved to complete the task",
                "values_from": "concept=Goal",
                "showInGrid": False,
                "isLink": False,
                "nullable": False,
                "topic": "Concept:Task",
                "regexp": None
              }
        property = Property(properties=data)
        expected_res = {
            "target": "Goal",
            "source": "Task",
            "source_cardinality": "*",
            "target_cardinality": "*",
            "property": property
        }
        u = property.is_used_for()
        res = UML.get_outgoing_edges(properties=[property], entity_name="Task")
        self.assertTrue(len(res) == 1)
        for key in expected_res.keys():
            self.assertEqual(res[0][key], expected_res[key])
        # Change Property inputType to test if cardinality is extracted correctly
        property.input_type = "combobox"
        res_2 = UML.get_outgoing_edges(properties=[property], entity_name="Task")
        self.assertEqual(res_2[0]["target_cardinality"], "1")
        # Test if only the properties of the given entity are used for the extraction
        self.assertTrue(len(UML.get_outgoing_edges(properties=[property], entity_name="NoTopic")) == 0)

    def testUMLIncomingEdges(self):
        data = {
                "Property": "Property:Task goals",
                "name": "Task goals",
                "label": "Goals",
                "type": "Special:Types/Page",
                "index": None,
                "sortPos": None,
                "primaryKey": False,
                "mandatory": False,
                "namespace": None,
                "size": None,
                "uploadable": False,
                "defaultValue": None,
                "inputType": "tokens",
                "allowedValues": None,
                "documentation": "Goals that must be achieved to complete the task",
                "values_from": "concept=Goal",
                "showInGrid": False,
                "isLink": False,
                "nullable": False,
                "topic": "Concept:Task",
                "regexp": None
              }
        property = Property(properties=data)
        expected_res = {
            "target": "Goal",
            "source": "Task",
            "source_cardinality": "*",
            "target_cardinality": "*",
            "property": property
        }
        u = property.is_used_for()
        res = UML.get_incoming_edges_reduced(properties=[property], entity_name="Goal")
        self.assertTrue(len(res) == 1)
        for key in expected_res.keys():
            self.assertEqual(res[0][key], expected_res[key])
        # Change Property inputType to test if cardinality is extracted correctly
        property.input_type = "combobox"
        res_2 = UML.get_incoming_edges_reduced(properties=[property], entity_name="Goal")
        self.assertEqual(res_2[0]["target_cardinality"], "1")
        # Test if only the properties of the given entity are used for the extraction
        self.assertTrue(len(UML.get_incoming_edges_reduced(properties=[property], entity_name="NoTopic")) == 0)

    def testUMLReducedIncomingEdges(self):
        data = [{
                "Property": "Property:Task goals",
                "name": "Task goals",
                "label": "Goals",
                "type": "Special:Types/Page",
                "index": None,
                "sortPos": None,
                "primaryKey": False,
                "mandatory": False,
                "namespace": None,
                "size": None,
                "uploadable": False,
                "defaultValue": None,
                "inputType": "tokens",
                "allowedValues": None,
                "documentation": "Goals that must be achieved to complete the task",
                "values_from": "concept=Goal",
                "showInGrid": False,
                "isLink": False,
                "nullable": False,
                "topic": "Concept:Project",
                "regexp": None
              },
            {
                "Property": "Property:Project goals",
                "name": "Project goals",
                "label": "Goals",
                "type": "Special:Types/Page",
                "index": None,
                "sortPos": None,
                "primaryKey": False,
                "mandatory": False,
                "namespace": None,
                "size": None,
                "uploadable": False,
                "defaultValue": None,
                "inputType": "tokens",
                "allowedValues": None,
                "documentation": "Goals that must be achieved to complete the task",
                "values_from": "concept=Goal",
                "showInGrid": False,
                "isLink": False,
                "nullable": False,
                "topic": "Concept:Project",
                "regexp": None
            }
        ]
        properties = [Property(p) for p in data]
        expected_res = {
            "target": "Goal",
            "source": "Project",
            "source_cardinality": "*",
            "target_cardinality": "*",
            "properties": ["Task goals", "Project goals"]
        }
        res = UML.get_incoming_edges_reduced(properties=properties, entity_name="Goal")
        self.assertTrue(len(res) == 1)
        for key in expected_res.keys():
            self.assertEqual(res[0][key], expected_res[key])
        # Test if only the properties of the given entity are used for the extraction
        self.assertTrue(len(UML.get_incoming_edges_reduced(properties=properties, entity_name="NoTopic")) == 0)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()