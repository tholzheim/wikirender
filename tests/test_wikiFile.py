import unittest

from wikifile.wikiFile import WikiFile


class TestWikiFile(unittest.TestCase):
    """
    Test the jinja template utils
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_template_name(self):
        self.assertEqual(WikiFile.get_template_name("   TestTemplate"), "TestTemplate",
                         "Whitespace at the beginning of template name was not removed")
        self.assertEqual(WikiFile.get_template_name("TestTemplate   "), "TestTemplate",
                         "Whitespace at the end of template name was not removed")
        self.assertEqual(WikiFile.get_template_name("   TestTemplate\n"), "TestTemplate",
                         "Whitespace at the beginning of template name was not removed")



if __name__ == "__main__":
    unittest.main()
