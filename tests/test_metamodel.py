'''
Created on 2021-03-27

@author: wf
'''
import unittest
from unittest import TestCase

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
        context = Context({"name": "MetaModel"})
        self.assertEqual("MetaModel", context.name)
        topic = None
        # try:
        #    topic=Topic({"name":"Context","label":"Context"})
        #    self.fail("there should be an exception")
        # except Exception as ex:
        #    self.assertTrue("Invalid property 'label'" in str(ex))
        self.assertIsNone(topic)
        topic = Topic({"name": "Context", "pluralName": "Contexts"})
        self.assertEqual("Context", topic.name)
        self.assertEqual("Contexts", topic.plural_name)
        prop = Property({"name": "name", "label": "name"})
        self.assertEqual("name", prop.name)
        self.assertEqual("name", prop.label)
        self.assertIsNone(prop.type)
        pass

    def testTopicFromJson(self):
        '''
        test loading/constructing from Json
        '''
        jsonStr = """{
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

        topics = Topic.fromJson(jsonStr)
        self.assertEqual(2, len(topics))
        commitTopic = topics[0]
        self.assertEqual("Commits", commitTopic.plural_name)
        taskTopic = topics[1]
        self.assertEqual("Task", taskTopic.name)

    def testPropertyFromJson(self):
        '''
        test loading/constructing from Json
        '''
        jsonStr = """{
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
        props = Property.fromJson(jsonStr)
        self.assertEqual(4, len(props))
        wprop = props[3]
        self.assertEqual("assigned to", wprop.label)
        # TODO: wait for Type handling !!!
        # self.assertFalse(wprop.show_in_grid)
        self.assertTrue("f" in wprop.show_in_grid)


class TestTopic(TestCase):
    def test_get_related_topics(self):
        # Test data containing one incoming and one outgoing edge from related topics
        data_properties = [{
                "Property": "Property:Task goals",
                "name": "Task goals",
                "label": "Goals",
                "type": "Special:Types/Page",
                "inputType": "tokens",
                "values_from": "concept=Goal",
                "topic": "Concept:Task"
            },
            {
                "Property": "Property:Task ",
                "name": "Task description",
                "label": "Goals",
                "type": "Special:Types/Page",
                "inputType": "tokens",
                "values_from": "property=Task description",
                "topic": "Concept:Task"
            },
            {
                "Property": "Property:Project tasks",
                "name": "Project tasks",
                "label": "Goals",
                "type": "Special:Types/Page",
                "inputType": "tokens",
                "values_from": "concept=Task",
                "topic": "Concept:Project"
            }
        ]
        properties = [Property(x) for x in data_properties]
        rel_topic_names = Topic(properties={"name": "Task", "pluralName": "Tasks"}).get_related_topics(properties)
        self.assertTrue(len(rel_topic_names) == 2)
        for name in rel_topic_names:
            self.assertTrue(name in ["Project", "Goal"])

    def test_render_entity(self):
        data = {"name": "Topic",
                "pluralName": "Topics",
                "icon": "File:Topic_icon.png",
                "iconUrl": "/images/a/ae/Index.png",
                "documentation": "A Topic is a Concept/Class/Thing/Entity",
                "wikiDocumentation": "A Topic is a Concept/Class/Thing/Entity",
                "context": "MetaModel"
                }
        exp_template_oneliner = "{{Topic|name=Topic|pluralName=Topics|icon=File:Topic_icon.png|iconUrl=/images/a/ae/Index.png|documentation=A Topic is a Concept/Class/Thing/Entity|wikiDocumentation=A Topic is a Concept/Class/Thing/Entity|context=MetaModel}}"
        exp_template_pretty = exp_template_oneliner.replace("|", "\n|").replace("}}", "\n}}")
        topic = Topic(properties=data)
        self.assertEqual(exp_template_oneliner, topic.render_entity(oneliner=True))
        self.assertEqual(exp_template_pretty, topic.render_entity(oneliner=False))


class TestProperty(TestCase):

    def test_get_property_properties(self):
        data = [{
            "name": "Property name",
            "type": "Special:Types/Text",
            "topic": "Concept:Property",
            "index": "2",
            "sortPos": "2"
        }, {
            "name": "Property label",
            "type": "Special:Types/Text",
            "topic": "Concept:Property",
            "index": "1",
            "sortPos": "1"
        }, {
            "name": "Property index",
            "type": "Special:Types/Number",
            "topic": "Concept:Property"
        }, {
            "name": "Property Page",
            "type": "Special:Types/Page",
            "topic": "Concept:Test3"
        }]
        properties = [Property(x) for x in data]
        property_properties = Property.get_property_properties(properties=properties)
        self.assertTrue(len(property_properties) == 3)
        for property in property_properties:
            self.assertEqual("Concept:Property", property.topic)
        # test sorting of properties
        self.assertEqual("Property label", property_properties[0].name)
        self.assertEqual("Property name", property_properties[1].name)
        self.assertEqual("Property index", property_properties[2].name)

    def test_get_entity_properties(self):
        data = [{
            "name": "Property text",
            "type": "Special:Types/Text",
            "topic": "Concept:Test"
        }, {
            "name": "Property boolean",
            "type": "Special:Types/Boolean",
            "topic": "Concept:Test"
        }, {
            "name": "Property Number",
            "type": "Special:Types/Number",
            "topic": "Concept:Test2"
        }, {
            "name": "Property Page",
            "type": "Special:Types/Page",
            "topic": "Concept:Test3"
        }]
        properties = [Property(x) for x in data]
        properties_test = Property.get_entity_properties(entity_name="Test", properties=properties)
        self.assertTrue(len(properties_test) == 2)
        for property in properties_test:
            self.assertEqual("Concept:Test", property.topic)

    def test_get_primitive_properties(self):
        data = [{
            "name": "Property text",
            "type": "Special:Types/Text",
            "topic": "Concept:Test"
        }, {
            "name": "Property boolean",
            "type": "Special:Types/Boolean",
            "topic": "Concept:Test"
        }, {
            "name": "Property Number",
            "type": "Special:Types/Number",
            "topic": "Concept:Test"
        }, {
            "name": "Property Page",
            "type": "Special:Types/Page",
            "topic": "Concept:NonPrimitiveProperty"
        }]
        properties = [Property(x) for x in data]
        primtive_properties = Property.get_primitive_properties(entity_name="Test", properties=properties)
        self.assertTrue(len(primtive_properties) == len(data) - 1)
        for property in primtive_properties:
            self.assertEqual(property.topic, "Concept:Test")

    def test_render_entity(self):
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
        exp_template_oneliner = "{{Property|name=Task goals|label=Goals|type=Special:Types/Page|primaryKey=false|mandatory=false|uploadable=false|inputType=tokens|documentation=Goals that must be achieved to complete the task|values from=concept=Goal|showInGrid=false|isLink=false|nullable=false|topic=Concept:Task}}"
        exp_template_pretty = exp_template_oneliner.replace("|", "\n|").replace("}}", "\n}}")
        property = Property(properties=data)
        self.assertEqual(exp_template_oneliner, property.render_entity(oneliner=True))
        self.assertEqual(exp_template_pretty, property.render_entity(oneliner=False))


class TestUML(TestCase):

    def test_get_outgoing_edges(self):
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

    def test_get_incoming_edges(self):
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

    def test_get_incoming_edges_reduced(self):
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
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
