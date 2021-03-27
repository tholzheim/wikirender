'''
Created on 2021-03-27

@author: wf
'''
import unittest
from wikifile.metamodel import Context, Topic,Property


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
        try:
            topic=Topic({"name":"Context","label":"Context"})
            self.fail("there should be an exception")
        except Exception as ex:
            self.assertTrue("Invalid property 'label'" in str(ex))
        self.assertIsNone(topic)
        topic=Topic({"name":"Context","pluralName":"Contexts"})    
        self.assertEqual("Context",topic.name)
        self.assertEqual("Contexts",topic.plural_name)
        prop=Property({"name":"name","label":"name"})
        self.assertEqual("name",prop.name)
        self.assertEqual("name",prop.label)
        self.assertIsNone(prop.type)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()