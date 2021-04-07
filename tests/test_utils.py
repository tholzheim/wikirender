import os
import unittest
from distutils.sysconfig import get_python_lib
import getpass
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


if __name__ == "__main__":
    unittest.main()
