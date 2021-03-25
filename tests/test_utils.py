import os
import unittest
from wikifile.wikiRender import WikiRender

class TestUtilsTemplate(unittest.TestCase):
    """
    Test the jinja template utils
    """

    def setUp(self):
        self.debug = False
        script_dir = os.path.dirname(os.path.abspath(__file__)) + "/.."
        # print(script_dir)
        self.templateEnv = WikiRender.getTemplateEnv(script_dir)

    def tearDown(self):
        pass

    def test_render_entity(self):
        name = "Event"
        properties = { 'Title': 'SMWCon', 'Year': '2020', 'Description': "test value test value\n with line break"}
        template2 = self.templateEnv.from_string(
            "{% from 'utils.jinja' import render_entity %}{{render_entity(name, properties)}}")
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
