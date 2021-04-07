'''
Created on 2021-03-27

@author: wf
'''
import json
import unittest
from unittest import TestCase

from wikifile.metamodel import Context, Topic, Property, UML, MetaModelElement


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
        self.assertEqual("Contexts", topic.pluralName)
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
    "pageTitle": "Concept:Commit",
    "name": "Commit",
    "pluralName": "Commits",
    "documentation": "A Git commit",
    "wikiDocumentation": "see https://git-scm.com/docs/git-commit",
    "cargo": "true"
  }]
}"""

        topic = Topic.from_wiki_json(jsonStr)
        self.assertTrue(isinstance(topic, Topic))
        self.assertEqual("Commits", topic.pluralName)
        self.assertEqual("Commit", topic.name)
        self.assertTrue(topic.cargo)

        # Test with properties
        json_props = """{ "data":[
            {
                "name":"property 1"
            },
            {
                "name":"property 2"
            },
            {
                "name":"property 3"
            }
        ]}"""
        prop_list = ["property 1","property 2","property 3"]
        topic_with_props = Topic.from_wiki_json(jsonStr, json_props)
        self.assertTrue(len(topic_with_props.properties) == 3)
        # Check if each item in properties is a Property and corresponds to exactly one of the given property configs
        for p in topic_with_props.properties:
            self.assertTrue(isinstance(p, Property))
            self.assertTrue(p.name in prop_list)
            prop_list.remove(p.name)

    def testPropertyFromJson(self):
        '''
        test loading/constructing from Json
        '''
        jsonStr = """{
        "data": 
[{
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
  }]
}"""
        props = Property.from_wiki_json(jsonStr)
        self.assertTrue(isinstance(props,Property))
        self.assertEqual("Goals", props.label)
        self.assertFalse(props.showInGrid)
        # check if null in converted to None
        self.assertIsNone(props.values_from)


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
        rel_topic_names = Topic({"name": "Task", "pluralName": "Tasks"}).get_related_topics(properties)
        self.assertTrue(len(rel_topic_names) == 2)
        for name in rel_topic_names:
            self.assertTrue(name in ["Project", "Goal"])

    def test_get_page_link(self):
        topic = Topic({"name": "Topic"})
        self.assertEqual("[[Concept:Topic]]", topic.get_page_link())
        topic.__dict__.update(pageTitle="Concept:Topic")
        self.assertEqual("[[Concept:Topic]]", topic.get_page_link())

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
        topic = Topic(data)
        self.assertEqual(exp_template_oneliner, topic.render_entity(oneliner=True))
        self.assertEqual(exp_template_pretty, topic.render_entity(oneliner=False))


class TestProperty(TestCase):

    def test_get_property_properties(self):
        #self.fail()
        # ToDo: Decide what the final Property properties are and test for them here
        property_properties = Property.get_property_properties()
        print(len(property_properties))
        self.assertTrue(len(property_properties) == 18)
        for property in property_properties:
            self.assertEqual("Property", property.topic)
        # test sorting of properties
        self.assertEqual("name", property_properties[0].name)
        self.assertEqual("label", property_properties[1].name)
        self.assertEqual("type", property_properties[2].name)

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

    def test_from_wiki_json(self):
        raw_data = {
            "data":[
                {
                "name": "Topic",
                "pluralName": "Topics",
                "listLimit": 42,
                "cargo": "f"
                }
            ]
        }
        topic = Topic.from_wiki_json(json.dumps(raw_data), None)
        self.assertEqual("Topic", topic.name)
        self.assertEqual("Topics", topic.pluralName)
        self.assertTrue(topic.listLimit == 42)
        self.assertFalse(topic.cargo)
        topic_with_properties = Topic.from_wiki_json(json.dumps(raw_data), json.dumps({"data":[{"name":"prop1"},{"name":"prop2"}]}))
        self.assertTrue(len(topic_with_properties.properties) == 2)

    def test_get_page_link(self):
        p = Property({"name": "title", "label": "Title", "pageTitle": "Property:Event title"})
        self.assertEqual("[[Property:Event title|Title]]", p.get_page_link())
        p_without_pageTitle = Property({"name": "title", "label": "Title"})
        self.assertEqual("[[Property:title|Title]]", p_without_pageTitle.get_page_link())
        p_without_label = Property({"name": "title", "pageTitle": "Property:Event title"})
        self.assertEqual("[[Property:Event title]]", p_without_label.get_page_link())

    def test_get_description_page_link(self):
        p = Property({"name":"title", "label": "Title", "pageTitle":"Property:Event title"})
        self.assertEqual("[[Event title::@@@|Title]]", p.get_description_page_link())
        p_without_pageTitle = Property({"name": "title", "label": "Title"})
        self.assertEqual("[[title::@@@|Title]]", p_without_pageTitle.get_description_page_link())
        p_without_label = Property({"name": "title", "pageTitle": "Property:Event title"})
        self.assertEqual("[[Event title::@@@]]", p_without_label.get_description_page_link())

    def test_query_entity_overview(self):
        topic = Topic({"name": "Test Title"})
        expected_query = """{{#ask:[[Topic name::Test Title]]
|mainlabel=-
|?Topic icon=icon
|?=Topic
|?Topic pluralName=pluralName
|?Topic documentation=documentation
}}"""
        actual_query = topic.query_entity_overview()
        self.assertEqual(expected_query, actual_query)

    def test_query_examples(self):
        topic = Topic({"name": "Test Title"})
        expected_query = "{{#ask:[[Concept:Test Title]]|limit=10|searchlabel=...more examples}}"
        actual_query = topic.query_examples(oneliner=True)
        self.assertEqual(expected_query, actual_query)

    def test_query_entity_properties(self):
        topic = Topic({"name":"Test Title"})
        expected_query = """{{#ask:[[Concept:Property]][[Used for::Concept:Test Title]]
|?name=name
|?label=label
|?type=type
|?index=index
|?sortPos=sortPos
|?primaryKey=primary key
|?mandatory=mandatory
|?namespace=namespace
|?size=size
|?uploadable=uploadable
|?defaultValue=default
|?inputType=inputType
|?allowedValues=allowedValues
|?documentation=documentation
|?values_from=values from
|?showInGrid=showInGrid
|?isLink=isLink
|?nullable=allow nulls?
|format=wikitable
}}"""
        actual_query = topic.query_entity_properties()
        self.assertEqual(expected_query, actual_query)


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
        property.inputType = "combobox"
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
        property.inputType = "combobox"
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


class TestMetaModelElement(TestCase):

    def test_from_properties(self):
        properties = {
            "name": "attrName",
            "label": "attrLabel",
            "pluralName": "attrPluralName"
        }
        # Check if only the names form the propList are used as attributes
        model = MetaModelElement(propList=["name"])
        model.fromProperties(properties)
        self.assertEqual("attrName", model.name)
        self.assertFalse("label" in model.__dict__)
        # check with extended propList
        model_2 = MetaModelElement(propList=["name", "label", "pluralName"])
        model_2.fromProperties(properties)
        self.assertEqual("attrName", model_2.name)
        self.assertEqual("attrLabel", model_2.label)
        self.assertEqual("attrPluralName", model_2.pluralName)

    def test_get_parameters(self):
        data = {
            "Valid key 1": "data",
            "Valid key 2": "data",
            "Invalid key 1": "invalid",
            "Valid key 3": "data",
            "Inalid key 2": "invalid"
        }
        expected_keys = ["Valid key 1","Valid key 2","Valid key 3"]
        reduced_data = MetaModelElement.get_parameters(data, expected_keys)
        self.assertEqual(expected_keys, list(reduced_data.keys()))
        for d in reduced_data.values():
            self.assertEqual("data", d)

    def test_get_prop_list_from_samples(self):
        samples = [{
            "test_key_1": "test_value_1",
            "test_key_2": "test_value_2",
            "test_key_3": "test_value_3",
            "test_key_4": "test_value_4",
        },
            {
                "test_key_5": "test_value_5",
                "test_key_6": "test_value_5",
            },
        ]
        expected_prop_list = ["test_key_1", "test_key_2", "test_key_3", "test_key_4", "test_key_5", "test_key_6", ]
        actual_prop_list = MetaModelElement.get_prop_list_from_samples(samples)
        self.assertTrue(len(expected_prop_list), len(actual_prop_list))
        for prop in actual_prop_list:
            self.assertTrue(prop in expected_prop_list)
