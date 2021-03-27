'''
Created on 2021-03-27

@author: th
'''
import unittest
from wikifile.smw import Query


class TestSMWQuery(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_smw_query(self):
        """test SMW Parts"""
        expected_query_oneliner = "{{#ask:[[Concept:Topic]]|mainlabel=Topic|?topic name=name|?topic pluralName=pluralName|?topic documentation}}"
        expected_query_pretty = "{{#ask:[[Concept:Topic]]\n|mainlabel=Topic\n|?topic name=name\n|?topic pluralName=pluralName\n|?topic documentation\n}}"
        query = Query(mainlabel="Topic")
        query.select("Concept:Topic")
        query.printout("topic name", "name")
        query.printout("topic pluralName", "pluralName")
        query.printout("topic documentation")
        self.assertEqual(expected_query_oneliner, query.render())
        self.assertEqual(expected_query_pretty, query.render(oneliner=False))
        # Test query parameter
        expected_query_oneliner_with_parameter = "{{#ask:[[Concept:Topic]]|mainlabel=Topic|limit=10|offset=5|format=count|searchlabel=Test query}}"
        expected_query_pretty_with_parameter = "{{#ask:[[Concept:Topic]]\n|mainlabel=Topic\n|limit=10\n|offset=5\n|format=count\n|searchlabel=Test query\n}}"
        query_para = Query(mainlabel="Topic", format="count", searchlabel="Test query", limit=10, offset=5)
        query_para.select("Concept:Topic")
        self.assertEqual(expected_query_oneliner_with_parameter, query_para.render())
        self.assertEqual(expected_query_pretty_with_parameter, query_para.render(oneliner=False))
        # Test sort parameter
        expected_sort_query = "{{#ask:[[Concept:Topic]]|mainlabel=Topic|?topic name|sort=topic name}}"
        query_sort = Query(mainlabel="Topic").select("Concept:Topic").printout("topic name").sort_by("topic name")
        self.assertEqual(expected_sort_query, query_sort.render())
        expected_sort_query_2 = "{{#ask:[[Concept:Topic]]|mainlabel=Topic|?topic name|?topic pluralName|sort=topic name,topic pluralName}}"
        query_sort.printout("topic pluralName").sort_by("topic name", "topic pluralName")
        self.assertEqual(expected_sort_query_2, query_sort.render())
        pass


if __name__ == "__main__":
    unittest.main()

