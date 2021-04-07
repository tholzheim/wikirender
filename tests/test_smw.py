from unittest import TestCase

from wikifile.metamodel import Property, Topic
from wikifile.smw import Query, Form, SMWPart, SMW, Table


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
        topic = Topic(topic_properties={"name": "Task", "pluralName": "Tasks"})
        smwParts = SMWPart.getAll(None)
        all_page_names = ["Category:Task", "Concept:Task", "Help:Task", "Template:Task", "Form:Task", "List of Tasks"]
        for part, smwPart in smwParts.items():
            page_name = smwPart.get_page_name(topic)
            self.assertTrue(page_name in all_page_names)
            all_page_names.remove(page_name)

    def test_getAllAsPageLink(self):
        expected_str = """*[[:List of Tests]]
*[[:Help:Test]]
*[[:Category:Test]]
*[[:Concept:Test]]
*[[:Form:Test]]
*[[:Template:Test]]
"""
        self.assertEqual(expected_str, SMWPart.getAllAsPageLink(Topic({"name": "Test", "pluralName": "Tests"})))


class TestForm(TestCase):
    def test_get_page_name(self):
        self.assertEqual("Form:Task", Form.get_page_name(Topic(topic_properties={"name": "Task", "pluralName": "Tasks"})))

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
        # test rendering of multiple tags
        exp_multi_tag = "{{{standard input|save}}}{{{standard input|preview}}}{{{standard input|cancel}}}"
        self.assertEqual(exp_multi_tag, Form.standard_input_tag(["save", "preview", "cancel"]))

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
            "primaryKey": True,
            "mandatory": False,
            "namespace": None,
            "size": None,
            "uploadable": True,
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

    def test_form_table(self):
        exp_form_table = """{| class="formtable InfoBox mw-collapsible" style="width:100%" 
|-
|colspan="2"  |Basic Information
|-
!style="text-align: left"  |[[Task goals::@@@|goals]]:
|{{{field|Task goals|input type=tokens|values from concept=Goal}}}
|-
!style="text-align: left"  |[[Task description::@@@|description]]<span style="color:#f00">*</span>:
|{{{field|description|input type=text}}}
|}"""
        data = [{
            "pageTitle": "Property:Task goals",
            "name": "Task goals",
            "label": "goals",
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
        },
            {
                "pageTitle": "Property:Task description",
                "name": "description",
                "label": "description",
                "type": "Special:Types/Test",
                "index": None,
                "sortPos": None,
                "primaryKey": False,
                "mandatory": True,
                "namespace": None,
                "size": None,
                "uploadable": False,
                "defaultValue": None,
                "inputType": "text",
                "allowedValues": None,
                "documentation": "Goals that must be achieved to complete the task",
                "values_from": None,
                "showInGrid": False,
                "isLink": False,
                "nullable": False,
                "topic": "Concept:Task",
                "regexp": None
            }
        ]
        properties = [Property(p) for p in data]
        actual_form_table = Form.form_table("Basic Information", properties)
        self.assertEqual(exp_form_table, actual_form_table)


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


class TestSMW(TestCase):

    def test_parser_function(self):
        expected_parser_function = "{{#switch:test|foo=Foo|baz=Baz|Bar}}"
        actual_parser_function = SMW.parser_function("switch", presence_is_true=True, test=True, foo="Foo", baz="Baz",
                                                     Bar=True)
        self.assertEqual(expected_parser_function, actual_parser_function)
        self.assertEqual("{{#test:test=Test|bool=true}}", SMW.parser_function("test", test="Test", bool=True))

    def test_render_entity(self):
        exp_oneliner = "{{Event|Title=SMWCon|Year=2020}}"
        exp_pretty = "{{Event\n|Title=SMWCon\n|Year=2020\n}}"
        self.assertEqual(exp_oneliner, SMW.render_entity("Event", **{"Title": "SMWCon", "Year": 2020}))
        self.assertEqual(exp_pretty, SMW.render_entity("Event", oneliner=False, **{"Title": "SMWCon", "Year": 2020}))

    def test_render_sample_entity_with_properties(self):
        exp_oneliner = "{{Event|EventTitle=Some Title|EventYear=Some Year}}"
        exp_pretty = "{{Event\n|EventTitle=Some Title\n|EventYear=Some Year\n}}"
        event = Topic({"pageName": "Concept:Event", "name": "Event", "pluralName": "Events"})
        properties = [Property({"pageName": "Property:Event title", "name": "EventTitle", "label": "Title"}),
                      Property({"pageName": "Property:Event year", "name": "EventYear", "label": "Year"})]
        self.assertEqual(exp_oneliner, SMW.render_sample_entity_with_properties(event, properties))
        self.assertEqual(exp_pretty, SMW.render_sample_entity_with_properties(event, properties, oneliner=False))

    def test_render_parameters(self):
        exp_oneliner = "|Title=Some Title|Year=2020|Foo=bar|isTrue=true"
        exp_pretty = "|Title=Some Title\n|Year=2020\n|Foo=bar\n|isTrue=true\n"
        parameters = {
            "Title": "Some Title",
            "Year": 2020,
            "Foo": "bar",
            "isTrue": True
        }
        self.assertEqual(exp_oneliner, SMW.render_parameters(oneliner=True, **parameters))
        self.assertEqual(exp_pretty, SMW.render_parameters(oneliner=False, **parameters))
        self.assertEqual(exp_oneliner.replace("=true", ""),
                         SMW.render_parameters(oneliner=True, presence_is_true=True, **parameters))
        self.assertEqual(exp_pretty.replace("=true", ""),
                         SMW.render_parameters(oneliner=False, presence_is_true=True, **parameters))

    def test_set_entity_parameter(self):
        exp_oneliner = "{{#set:isA=Event|Event title={{{EventTitle|}}}|Event year={{{EventYear|}}}}}"
        exp_pretty = "{{#set:isA=Event\n|Event title={{{EventTitle|}}}\n|Event year={{{EventYear|}}}\n}}"
        event = Topic({"name": "Event", "pluralName": "Events"})
        event = Topic({"pageTitle": "Concept:Event", "name": "Event", "pluralName": "Events"})
        properties = [Property({"pageTitle": "Property:Event title", "name": "EventTitle", "label": "Title"}),
                      Property({"pageTitle": "Property:Event year", "name": "EventYear", "label": "Year"})]
        self.assertEqual(exp_oneliner, SMW.set_entity_parameter(event, properties, oneliner=True))
        self.assertEqual(exp_pretty, SMW.set_entity_parameter(event, properties, oneliner=False))

    def test_render_as_list(self):
        exp_simple = "*item1\n*item2\n*item3\n"
        exp_advanced = "*item1\n**item11\n**item12\n**item13\n*item2\n**item21\n***item211\n*item3\n"
        data_simple = ["item1", "item2", "item3"]
        data_advanced = ["item1", ["item11", "item12", "item13"], "item2", ["item21", ["item211"]], "item3"]
        self.assertEqual(exp_simple, SMW.render_as_list(data_simple))
        self.assertEqual(exp_advanced, SMW.render_as_list(data_advanced))
        self.assertEqual(exp_simple.replace("*", "#"), SMW.render_as_list(data_simple, is_ordered=True))
        self.assertEqual(exp_advanced.replace("*", "#"), SMW.render_as_list(data_advanced, is_ordered=True))


class TestTable(TestCase):

    def test_add_row(self):
        table_style = {"css_class": "wikitable", "style": "width:100%"}
        table = Table(**table_style)
        table.add_row(css_class="Row_1")
        table.add_row(css_class="Row_2")
        self.assertTrue(len(table.rows) == 2)
        # check order of the rows
        self.assertEqual("Row_1", table.rows[0].css_class)
        self.assertEqual("Row_2", table.rows[1].css_class)

    def test_render(self):
        table_style = {"css_class": "wikitable", "style": "width:100%"}
        row_style = {"style": "color:red"}
        cell_style = {"style": "color:blue"}
        table = Table(**table_style)
        first = table.add_row(**row_style)
        first.add_cell("col 1; row 1", is_header=True)
        first.add_cell("col 2; row 1", is_header=True)
        second = table.add_row()
        second.add_cell("col 1; row 2", is_header=True)
        second.add_cell("col 2; row 2", **cell_style)
        third = table.add_row()
        third.add_cell("Test Table", colspan=2)
        exp_table = """{| class="wikitable" style="width:100%" 
|-style="color:red" 
!col 1; row 1
!col 2; row 1
|-
!col 1; row 2
|style="color:blue"  |col 2; row 2
|-
|colspan="2"  |Test Table
|}"""
        self.assertEqual(exp_table, table.render())


class TestRow(TestCase):
    """Test behavior of the internal class of class Table"""

    def test_add_cell(self):
        row = Table.Row(css_class="RowStyle", style="color:red")
        row.add_cell("Test value header", css_class="Test class", style="color:red", is_header=True, colspan=2)
        row.add_cell("Test value", css_class="Test class", style="color:red")
        self.assertTrue(len(row.cells) == 2)
        # Check order of the cells
        self.assertEqual("Test value header", row.cells[0].content)
        self.assertEqual("Test value", row.cells[1].content)

    def test_render(self):
        row = Table.Row(css_class="RowStyle", style="color:red")
        row.add_cell("Test value header", css_class="Test class", style="color:red", is_header=True, colspan=2)
        row.add_cell("Test value", css_class="Test class", style="color:red")
        exp_val = """|-class="RowStyle" style="color:red" 
!class="Test class" style="color:red" colspan="2"  |Test value header
|class="Test class" style="color:red"  |Test value
"""
        self.assertEqual(exp_val, row.render())


class TestCell(TestCase):
    """Test behavior of the internal class of class Table"""

    def test_render(self):
        cell = Table.Row.Cell("Test value", css_class="Test class", style="color:red")
        exp_val = '|class="Test class" style="color:red"  |Test value'
        self.assertEqual(exp_val, cell.render())
        cell_header = Table.Row.Cell("Test value", css_class="Test class", style="color:red", is_header=True, colspan=2)
        exp_val_2 = '!class="Test class" style="color:red" colspan="2"  |Test value'
        self.assertEqual(exp_val_2, cell_header.render())

