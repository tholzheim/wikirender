'''
Created on 2021-03-27

@author: th
'''
import unittest

from wikifile.smw import Query, Form


class TestSMWForm(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_form_standard_input_tag(self):
        """
        test form standard input tag
        """
        exp_tag = "{{{standard input|save|label=Save Page|class =test|style=width:100%}}}"
        self.assertEqual(exp_tag, Form.standard_input_tag("save", label="Save Page", class_="test", style="width:100%", ))
        # test invalid input tag
        self.assertRaises(AttributeError, Form.standard_input_tag, "invalid tag that should raise an error")
        pass

    def test_form_forminput(self):
        """
        test form forminput parser function
        """
        expected_forminput = "{{#forminput:|form=Event|size=25|placeholder=Enter Event|popup}}"
        self.assertEqual(expected_forminput, Form.forminput(form="Event", size=25, placeholder="Enter Event", popup=True))

if __name__ == "__main__":
    unittest.main()