'''
Created on 2021-03-07

@author: wf
'''
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from wikifile.wikiRender import WikiRender
    from wikifile.metamodel import Topic, Property, UML, Context


class SMWPart(object):
    '''
    a technical Semantic MediaWiki Part
    '''

    def __init__(self, part, wikiRender=None):
        '''
        Constructor
        '''
        self.part = part
        self.wikiRender = wikiRender
        self.template = "%s_page.jinja" % part.lower().replace(" ", "_")

    def render_page(self, topic: Topic):
        """
        Renders the help page for the given entity using the provided properties
        Args:
            topic: topic for which the page should be rendered
            properties: list of all properties
        Returns:

        """
        template_template = self.wikiRender.template_env.get_template(self.template)
        page = template_template.render(topic=topic)
        return page

    @staticmethod
    def getAll(wikiRender: WikiRender):
        smwPartList = [
            ListOf(wikiRender),
            SMWPart("Help"),
            SMWPart("Category"),
            SMWPart("Concept"),
            Form(wikiRender),
            Template(wikiRender),
            #TODO: implement
            #SMWPart("Properties"),
            #SMWPart("PythonCode")
        ]
        smwParts = {}
        for smwPart in smwPartList:
            smwPart.wikiRender = wikiRender
            smwParts[smwPart.part] = smwPart
        return smwParts

    def get_page_name(self, topic: Topic):
        return f"{self.part}:{topic.name}"

    @staticmethod
    def getAllAsPageLink(topic: Topic):
        """Returns all technical pages of the given topic as link list (also known as the see also section)"""
        return SMW.render_as_list([f"[[:{smwPart.get_page_name(topic)}]]" for smwPart in SMWPart.getAll(None).values()])


class SMW:
    """Provides functions covering basic SMW features"""

    @staticmethod
    def parser_function(function_name: str, presence_is_true=False, **kwargs):
        """
        Renders the given parameters and function name to the corresponding SMW parser function.
        Parameter names containing a whitespace must be written with an underscore instead.
        Args:
            function_name: name of the function
            presence_is_true: If true only the name of bool parameters is displayed. Otherwise the bool value is printed out.
            **kwargs: parameters of the parser function

        Returns:

        """
        return "{{#" + function_name + ":" + SMW.render_parameters(presence_is_true=presence_is_true, **kwargs)[1:] + "}}"

    @staticmethod
    def render_entity(template: str, oneliner=True, **kwargs):
        """
        Renders the given parameters as template of the given name.
        Args:
            template: name of the template
            oneliner= If True entity is returned in oneliner. Otherwise the entity is rendered in a prettier format.
            **kwargs: parameters of the template
        Returns:

        Example:
            Args:
                template="Event"
                oneliner= False
                kwargs= 'Title'='SMWCon', 'Year'='2020'
            Returns:
                    {{Event
                    |Title= SMWCon
                    |Year= 2020
                    }}
        """
        separator = "" if oneliner else "\n"
        return "{{" + template + separator + SMW.render_parameters(oneliner=oneliner, **kwargs) + "}}"

    @staticmethod
    def render_sample_entity_with_properties(topic: Topic, properties: list, oneliner=True):
        """

        Args:
            topic: Topic for which the sample entity template should be generated
            properties: properties of the topic
            oneliner: If true the result will be in one line. Otherwise, result string is returned in a prettier format.
        Returns:

        Example:
            Args:
                template="Event"
                properties= [<Title property>, <Year property>]
                oneliner= False
            Returns:
                    {{Event
                    |Title= Some Title
                    |Year= Some Year
                    }}
        """
        property_dict = {}
        for property in properties:
            property_dict = {**property_dict, property.name: f"Some {property.label}"}
        return SMW.render_entity(topic.name, oneliner=oneliner, **property_dict)

    @staticmethod
    def render_parameters(oneliner=True, presence_is_true=False, **kwargs):
        """

        Args:
            oneliner: If true parameters are rendered in one line.
            presence_is_true: If true only the name of bool parameters is displayed. Otherwise the bool value is printed out.
            **kwargs: All paramerters with there values. If a parameter has a whitespace escape it with an underscore.
        Returns:
            Returns the given parameters as rendered mediawiki template parameters
        """
        separator = "" if oneliner else "\n"
        res = ""
        for parameter, value in kwargs.items():
            if isinstance(value, bool):
                label = parameter.replace("_", " ")
                if presence_is_true:
                    if value:
                        res += f"|{label}{separator}"
                else:
                    # ToDo: Update bool values if decided how to query wiki config
                    bool_value = "true" if value else "false"
                    res += f"|{label}={bool_value}{separator}"
            elif value is not None:
                label = parameter.replace("_", " ")
                res += f"|{label}={value}{separator}"
        return res

    @staticmethod
    def set_entity_parameter(topic, properties, oneliner=True, withDescription=False):
        """

        Args:
            topic: topic for which the properties should be set
            properties: properties which should be stored
            oneliner: If true the result will be in one line. Otherwise, result string is returned in a prettier format.

        Returns:
        """
        property_dict = {"isA": topic.name}
        for property in properties:
            property_dict = {**property_dict, property.get_pageTitle(withNamespace=False): "{{{" + property.name + "|}}}"}
        return SMW.parser_function("set", oneliner=oneliner, **property_dict)

    @staticmethod
    def render_as_list(data: list, is_ordered=False, prefix=""):
        """
        Renders the given data as mediawiki list. If a value in the data is also a list a sublist entry is generated.
        Args:
            data: data that should be rendered as list. Can also contain lists.
            is_ordered: If true an ordered list is returned based on the order in the given data. Otherwise, unordered list is returned.
            prefix: string that is placed before each list item
        Returns:

        """
        symbol = prefix
        symbol += "#" if is_ordered else "*"
        res = ""
        for d in data:
            if isinstance(d, list):
                res += SMW.render_as_list(d, is_ordered, symbol)
            else:
                res += f"{symbol}{d}\n"
        return res


class Template(SMWPart):
    """
    Provides methods to generate a Template page for a topic
    """

    def __init__(self, wikiRender=None):
        if wikiRender is not None:
            wikiRender.template_env.globals['Template'] = self
        super().__init__("Template", wikiRender)

    @staticmethod
    def get_page_name(topic: Topic):
        return f"Template:{topic.name}"

    @staticmethod
    def template_arg(arg):
        return "{{{" + arg + "|}}}"

    @staticmethod
    def table_of_arguments(topic: Topic, properties: list, clickable_links=True):
        """
        ToDo
        Args:
            topic:
            properties:

        Returns:

        """
        formlink = Form.formlink(form=topic.name, link_text="✎", target="{{FULLPAGENAME}}", tooltip="Start editing this " + topic.name)
        table_str = "{| class='wikitable'\n! colspan=2 | " + formlink + topic.get_page_link()+ "\n|-\n"
        sortBySortPos = lambda property: 99999 if "sortPos" not in property.__dict__ or property.__dict__.get(
            "sortPos") is None else int(property.sortPos)
        properties_sorted = sorted(properties, key=sortBySortPos)
        for property in properties_sorted:
            # ToDo: refactor Table definition
            label = property.get_description_page_link() if clickable_links else property.label
            table_str += "!style=\"text-align:left\" |" + label + "\n"
            table_str += "| {{#if:" + Template.template_arg(property.name) + "|" + Template.template_arg(property.name) + "|}}\n"
            table_str += "|-\n"
        return table_str + "|}"


class ListOf(SMWPart):
    """
    Provides methods to generate a List of page for a topic
    """

    def __init__(self, wikiRender=None):
        super().__init__("List of", wikiRender)

    @staticmethod
    def get_page_name(topic: Topic):
        return f"List of {topic.pluralName}"


class Form(SMWPart):
    """
    Provides methods to render a complete Form or parts of a Form.
    For more details see: https://www.mediawiki.org/wiki/Extension:Page_Forms
    """

    regexps = {
        'Regexp:NaturalNumber': {
            'regexp': "/^[0-9]+$!^$/",
            'message': 'Must be a Number',
            'or char': '!'
        }
    }

    def __init__(self, wikiRender=None):
        if wikiRender is not None:
            wikiRender.template_env.globals['Form'] = self
        super().__init__("Form", wikiRender)
        #self.template = "event_form.jinja"

    @staticmethod
    def get_page_name(topic: Topic):
        return f"Form:{topic.name}"

    @staticmethod
    def page_form_function(tag, **kwargs):
        """
        ToDo
        Args:
            tag: Type of the form function. e.g.: field, form, info, ...
            **kwargs: parameters of the form function
        Returns:

        """
        return "{{{" + tag + SMW.render_parameters(presence_is_true=True, **kwargs) + "}}}"

    @staticmethod
    def standard_input_tag(input, oneliner=True, **kwargs):
        """
        Renders standard input tag
        For more detail see: https://www.mediawiki.org/wiki/Extension:Page_Forms/Defining_forms#'standard_input'_tag
        Args:
            input: If list the standard input tag is generated for each item in the list with the given parameters. Otherwise, the standart input tag is generatde for the given input
            oneliner: If true result will beone string line. Otherwise, multiple standard input tags will result in multiple lines.
            **kwargs: parameters of the standard input tag. If the parameter contains whitespace escape it with underscore.
        Returns:
        """
        if isinstance(input, list):
            res = ""
            for tag in input:
                res += Form.standard_input_tag(tag, oneliner, **kwargs)
            return res
        else:
            postfix = "" if oneliner else "\n"
            possible_input_tags = ["save", "preview", "save and continue", "changes", "summary", "minor edit", "watch", "cancel"]
            if input not in possible_input_tags:
                tags = ','.join(possible_input_tags)
                raise AttributeError(f"Form standard input \"{input}\" was given but must be one of the following values:{tags}")
            return Form.page_form_function(tag="standard input", **{input:True, **kwargs}) + postfix

    @staticmethod
    def forminput(**kwargs):
        """
        Renders a forminput parser function with the given input
        For more details see: https://www.mediawiki.org/wiki/Extension:Page_Forms/Linking_to_forms#Using_#forminput
        Args:
            **kwargs: parameters of the forminput
        Returns:
        """
        return SMW.parser_function(function_name="forminput", presence_is_true=True, **kwargs)

    @staticmethod
    def formlink(**kwargs):
        """
        Renders a formlink parser function with the given input
        For more details see: https://www.mediawiki.org/wiki/Extension:Page_Forms/Linking_to_forms#Using_#formlink
        Args:
            **kwargs: parameters of the formlink
        Returns:

        """
        return SMW.parser_function(function_name="formlink", presence_is_true=True, **kwargs)

    @staticmethod
    def field(property: Property):
        """
        Get the form field of the given property
        Args:
            property: property for which the field should be rendered
        Returns:
            Returns a form field of given property
        """
        prop_map = {"inputType": "input_type",
                    "placeholder": "placeholder",
                    "defaultValue": "default",
                    "values_from": "values_from",
                    "uploadable": "uploadable",
                    "primaryKey": "unique",
                    "allowedValues": "values"}
        parameters = {}
        for prop in prop_map.keys():
            if prop == "inputType":
                if property.__dict__[prop] is None:
                    property.__dict__[prop] = "text"
                elif property.__dict__[prop].lower() == "textarea":
                    parameters["editor"] = "wikieditor"
            if prop in property.__dict__ and property.__dict__[prop] is not None:
                if prop == "values_from":
                    # values_from contains data like "concept=Country" so we add an auxiliary property "values from concept" with the value "Country"
                    vals = property.__dict__[prop].split("=")
                    parameters[f"{prop_map[prop]} {vals[0]}" ] = vals[1]
                else:
                    parameters[prop_map[prop]] = property.__dict__[prop]
                if prop == "inputType" and property.__dict__[prop] == "regexp":
                    parameters.update(Form.regexps.get(property.regexp))
        return Form.page_form_function(tag="field", **{property.name: True, **parameters})

    @staticmethod
    def form_table(label: str, properties: list, is_collapsible=True, ):
        """
        Generate a form table based on the given parameters.
        Note: the result is not a complete form (start and end tags are missing)   # ToDo: Since the result is not complete form consider renaming this method to field_table
        Args:
            label: Headline of the table
            properties: List of properties for which a field should be added to the form table
            is_collapsible: If true the table is collapsible. Other wise the table will be static
        Returns:
            Returns a table containing form fields based on the given properties
        """
        # Define styling
        table_style = {"css_class": "wikitable", "style": "width:100%"}
        if is_collapsible:
            table_style["css_class"] += " mw-collapsible"
        field_label_style = {"style": "text-align: left"}
        # Define the table
        table = Table(**table_style)
        # Add table headline
        if label:
            table.add_row().add_cell(content=label, colspan=2)
        # Add form field for each given property
        sortBySortPos = lambda property: 99999 if "sortPos" not in property.__dict__ or property.__dict__.get("sortPos") is None else int(property.sortPos)
        properties_sorted = sorted(properties, key=sortBySortPos)
        for property in properties_sorted:
            property_row = table.add_row()
            # Add field label
            field_label = property.get_description_page_link()
            if property.mandatory:
                field_label += "<span style=\"color:#f00\">*</span>"
            field_label += ":"
            property_row.add_cell(content=field_label, is_header=True, **field_label_style)
            # Add field
            property_row.add_cell(content=Form.field(property))
        return table.render()



class Query:
    """
    SMW Query
    """

    def __init__(self,
                 mode="ask",
                 mainlabel=None,
                 limit: int = None,
                 offset: int = None,
                 searchlabel: str = None,
                 outro: str = None,
                 intro: str = None,
                 default: str = None,
                 format: str = None,
                 headers: str = None,
                 order: str = None,
                 template: str = None):
        """
        Intit a Query with the given parameters
        Args:
            mode: ask for multi page query / show for single page query
            mainlabel: title of the first column
            limit: maximal number of pages selected
            offset: where to start selecting pages
            searchlabel: text for continuing the search
            outro: text that is appended to the output, if at least some results exist
            intro: initial text that prepends the output, if at least some results exist
            default: if, for any reason, the query returns no results, this will be printed instead
            format: output format  of the query
            headers: Show headers (with links), plain headers (just text) or hide them. show is default. Possible values show, hide and, plain.
            order: defines how results should be ordered, ascending is the default. Possible values ascending/asc, descending/desc/reverse, random/rand.
        """
        self.mode = mode
        self.page_selections = []
        self.printout_statements = []
        self.mainlabel = mainlabel
        self.limit = limit
        self.offset = offset
        self.searchlabel = searchlabel
        self.outro = outro
        self.intro = intro
        self.default = default
        self.format = format
        self.headers = headers
        self.order = order
        self.sort = None
        self.template= template
        self.parameters = ["limit", "offset", "format", "searchlabel", "outro", "intro", "default", "headers", "sort", "order", "template"]

    def render(self, oneliner=True):
        """
        Render this query to the string format of an SMW query
        Args:
            oneliner: If True the query is rendered into one line. Otherwise the query is rendered in a prettier format.
        Returns:
            Returns SMW query of this query object
        """
        separator = ""
        if not oneliner:
            separator = "\n"
        query = "{{#" + self.mode + ":"
        for selector in self.page_selections:
            query += f"[[{selector}]]"
        query += separator
        if self.mainlabel is not None:
            query += f"|mainlabel={self.mainlabel}{separator}"
        for printout_statement in self.printout_statements:
            query += f"|{printout_statement.render()}{separator}"
        for parameter in self.parameters:
            if self.__dict__[parameter] is not None:
                query += f"|{parameter}={self.__dict__[parameter]}{separator}"
        return query + "}}"

    def printout(self, property, label=None):
        """
        Add a printout statement to the query. Results in querying the given property name.
        Args:
            property: Name of the property that should be queried OR Property object that should be queried
            label: Label that should be displayed at the result

        Returns:
            Returns the query itself
        """
        if isinstance(property, str):
            self.printout_statements.append(self.PrintoutStatement(property, label))
        else:
            self.printout_statements.append(self.PrintoutStatement(property.get_pageTitle(withNamespace=False), label))
        return self

    def select(self, selector):
        """
        Add page selector to the query
        Args:
            selector:

        Returns:
            Returns the query itself
        """
        self.page_selections.append(selector)
        return self

    def printout_list_of_properties(self, properties: list, withNamespace=False):
        """
        Add a printout statement for each property of the given properties
        Args:
            properties: All properties that should be queried
        Returns:
            The query object itself
        """
        for property in properties:
            self.printout(property.get_pageTitle(withNamespace), property.label)
        return self

    def sort_by(self, *properties):
        """
        Set the sort parameter of the query. If already set it overwrites the existing parameter.
        Args:
            *properties:

        Returns:

        """
        self.sort = ", ".join(properties)
        return self

    class PrintoutStatement:
        """Printout statement of a SMW query"""

        def __init__(self, property_name, label=None):
            """
            Init the printout statement
            Args:
                property_name: Name of the property that should be queried
                label: Label that should be displayed at the result
            """
            self.property_name = property_name
            self.label = label

        def render(self):
            """
            Render this PrintoutStatement to the string format of an printout statement
            Returns:

            """
            label = f"={self.label}" if self.label else ""
            return f"?{self.property_name}{label}"


class Table:
    """
    Experimental Class to test if generating MediaWiki tables can be streamlined
    Provides methods to generate a MediaWiki table
    For more information see https://www.mediawiki.org/wiki/Help:Tables
    """

    def __init__(self, css_class: str=None, style: str=None ):
        """
        Initialize the table with the given style/ style class
        Args:
            css_class: css class the table should have
            style: individual css styles that should be applied to the class such as "width:100%"
        """
        self.rows = []
        self.css_class = css_class
        self.style = style

    def render(self):
        """Renders this table as wiki table"""
        res =  "{| " + Table.render_parameter(self.css_class, self.style) +"\n"
        for row in self.rows:
            res += row.render()
        return res + "|}"

    def add_row(self, css_class: str=None, style: str=None, **kwargs):
        """
        Add a row to this table with the given styling configs
        Args:
            css_class: css class that the row should have
            style: individual css style that should be applied dto the row
            **kwargs: Additional parameter that should be set
        Returns:
            Returns the row object that was added to the table.
        """
        row = self.Row(css_class, style, **kwargs)
        self.rows.append(row)
        return row

    @staticmethod
    def render_parameter(css_class: str=None, style: str=None, **kwargs):
        """Render given parameter to the syntax of wiki tables"""
        res = ""
        res += f"class=\"{css_class}\" " if css_class else ""
        res += f"style=\"{style}\" " if style else ""
        for key, value in kwargs.items():
            if value:
                res += f"{key}=\"{value}\" "
        return res

    class Row:
        """
        Representing a row of a wiki table
        """

        def __init__(self, css_class: str=None, style: str=None):
            """
            Initialize table row with the given row style
            Args:
                css_class: css class of this row
                style: individual css style that should be applied to the row
            """
            self.cells = []
            self.css_class = css_class
            self.style = style

        def render(self):
            """Render this row as wiki table row"""
            res = "|-" + Table.render_parameter(self.css_class, self.style) +"\n"
            for cell in self.cells:
                res += cell.render() + "\n"
            return res[:-1] + "\n"

        def add_cell(self, content, is_header=False, colspan=None, css_class: str=None, style: str=None):
            """
            Add a cell to this row. The order of inserting cells corresponds to the ordering in the rendered table.
            First cell added is first column in the table.
            Args:
                content: Content of the cell
                is_header: True if this cell is a header cell.
                colspan: span of the cell
                css_class: css class of this cell
                style: individual css style that should be applied to the cell
            Returns:

            """
            cell = self.Cell(content, is_header, colspan, css_class, style)
            self.cells.append(cell)

        class Cell:
            """
            Representing a cell of a wiki table
            """
            def __init__(self, content, is_header=False, colspan: int=None, css_class: str=None, style: str=None):
                """
                Initialize table cell with the given content and style configs
                Args:
                    content: Content of the cell
                    is_header: True if this cell is a header cell.
                    colspan: span of the cell
                    css_class: css class of this cell
                    style: individual css style that should be applied to the cell
                """
                self.content = content
                self.is_header = is_header
                self.colspan = colspan
                self.css_class = css_class
                self.style = style

            def render(self):
                """Render this cell as wiki table cell"""
                separator = "!" if self.is_header else "|"
                config = Table.render_parameter(self.css_class, self.style, colspan=self.colspan)
                config += " |" if config else ""
                return f"{separator}{config}{self.content}"

