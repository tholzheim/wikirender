from unittest import TestCase

from wikifile.metamodel import Property, Topic
from wikifile.smw import Query, Form, SMWPart


class TestSMWPart(TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSMWPart(self):
        '''
        test SMW Parts
        '''
        pass

    def test_render_page(self):
        pass

    def test_get_all(self):
        smwParts = SMWPart.getAll(None)
        self.assertEqual(6, len(smwParts))
        self.assertEqual("list_of_page.jinja", smwParts["List of"].template)

    def test_get_page_name(self):
        topic = Topic(properties={"name": "Task", "pluralName": "Tasks"})
        smwParts = SMWPart.getAll(None)
        all_page_names = ["Category:Task", "Concept:Task", "Help:Task", "Template:Task", "Form:Task", "List of Tasks"]
        for part, smwPart in smwParts.items():
            page_name = smwPart.get_page_name(topic)
            self.assertTrue(page_name in all_page_names)
            all_page_names.remove(page_name)

class TestForm(TestCase):
    def test_get_page_name(self):
        self.assertEqual("Form:Task", Form.get_page_name(Topic(properties={"name": "Task", "pluralName": "Tasks"})))

    def test_page_form_function(self):
        exp_tag = "{{{form|label=Save Page|class =test|style=width:100%}}}"
        self.assertEqual(exp_tag,
                         Form.page_form_function("form", label="Save Page", class_="test", style="width:100%"))

    def test_standard_input_tag(self):
        exp_tag = "{{{standard input|save|label=Save Page|class =test|style=width:100%}}}"
        self.assertEqual(exp_tag,
                         Form.standard_input_tag("save", label="Save Page", class_="test", style="width:100%"))
        # test invalid input tag
        self.assertRaises(AttributeError, Form.standard_input_tag, "invalid tag that should raise an error")

    def test_forminput(self):
        expected_forminput = "{{#forminput:form=Event|size=25|placeholder=Enter Event|popup}}"
        self.assertEqual(expected_forminput,
                         Form.forminput(form="Event", size=25, placeholder="Enter Event", popup=True))

    def test_formlink(self):
        expected_formlink = "{{#formlink:form=Event|link text=Here|link type=button|query string=Event[Acronym]={{PAGENAME}}|target={{PAGENAME}}|tooltip=Edit here|popup|reload|new window|returnto={{PAGENAME}}}}"
        actual_formlink = Form.formlink(form="Event",
                                        link_text="Here",
                                        link_type="button",
                                        query_string="Event[Acronym]={{PAGENAME}}",
                                        target="{{PAGENAME}}",
                                        tooltip="Edit here",
                                        popup=True,
                                        reload=True,
                                        new_window=True,
                                        returnto="{{PAGENAME}}")
        self.assertEqual(expected_formlink, actual_formlink)

    def test_field(self):
        test_field = "{{{field|Country|input type=combobox|placeholder=e.g Germany|values from concept=Country|uploadable|unique}}}"
        data = {
            "property": "Property:Has location country",
            "name": "Country",
            "label": "Country",
            "type": "Special:Types/Page",
            "index": None,
            "sortPos": None,
            "primaryKey": False,
            "mandatory": False,
            "namespace": None,
            "size": None,
            "uploadable": False,
            "defaultValue": None,
            "inputType": "combobox",
            "allowedValues": None,
            "documentation": "Used to describe the country where something is located in.",
            "values_from": "concept=Country",
            "showInGrid": False,
            "isLink": False,
            "nullable": False,
            "topic": None,
            "regexp": None,
            "used_for": "Concept:Event",
            "placeholder": "e.g Germany"
        }
        property = Property(data)
        self.assertEqual(test_field, Form.field(property))


class TestQuery(TestCase):

    def test_render(self):
        query = Query("show", mainlabel="Test", searchlabel="Test searchlabel", limit=10, offset=5, format="table",
                      default="Test default", outro="Test outro", intro="Test intro", headers="Test headers",
                      order="asc")
        query.select("Concept:Test").select("Modificationdate::>2020")
        query.printout("name").printout("label", "l")
        query.sort_by("name", "label")
        expected_query_oneliner = "{{#show:[[Concept:Test]][[Modificationdate::>2020]]|mainlabel=Test|?name|?label=l|limit=10|offset=5|format=table|searchlabel=Test searchlabel|outro=Test outro|intro=Test intro|default=Test default|headers=Test headers|sort=name, label|order=asc}}"
        self.assertEqual(expected_query_oneliner, query.render(oneliner=True))
        expected_query_pretty = """{{#show:[[Concept:Test]][[Modificationdate::>2020]]
|mainlabel=Test
|?name
|?label=l
|limit=10
|offset=5
|format=table
|searchlabel=Test searchlabel
|outro=Test outro
|intro=Test intro
|default=Test default
|headers=Test headers
|sort=name, label
|order=asc
}}"""
        self.assertEqual(expected_query_pretty, query.render(oneliner=False))

    def test_printout(self):
        query = Query().printout("Modification date", "modified at")
        self.assertTrue(len(query.printout_statements) == 1)

    def test_select(self):
        query = Query().select("Concept:Event")
        self.assertTrue(len(query.page_selections) == 1)

    def test_sort_by(self):
        query = Query().sort_by("Property name", "Property label", "Property index")
        self.assertEqual("Property name, Property label, Property index", query.sort)
        # test overwriting of sort by attribute by calling the method again
        query = Query().sort_by("Property name")
        self.assertEqual("Property name", query.sort)


