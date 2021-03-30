'''
Created on 2021-03-07

@author: wf
'''
from wikifile.metamodel import Topic, Property
from wikifile.wikiRender import WikiRender


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

    def render_page(self, topic: Topic, properties: list):
        """
        Renders the help page for the given entity using the provided properties
        Args:
            topic: topic for which the page should be rendered
            properties: list of all properties
        Returns:

        """
        template_template = self.wikiRender.template_env.get_template(self.template)
        page = template_template.render(topic=topic, properties=properties)
        return page

    @staticmethod
    def getAll(wikiRender: WikiRender):
        smwPartList = [
            SMWPart("Category"),
            SMWPart("Concept"),
            Form(wikiRender),
            SMWPart("Template"),
            SMWPart("Help"),
            ListOf(wikiRender),
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
        Example:
            Args:
                template="Event"
                oneliner= If True entity is returned in oneliner. Otherwise the entity is rendered in a prettier format.
                kwargs= 'Title'='SMWCon', 'Year'='2020'
            Returns:
                    {{Event
                    |Title= SMWCon
                    |Year= 2020
                    |}
        Args:
            template: name of the template
            **kwargs: parameters of the template

        Returns:

        """
        separator = "" if oneliner else "\n"
        return "{{" + template + separator + SMW.render_parameters(oneliner=oneliner, **kwargs) + "}}"

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
                    res += f"|{label}{separator}"
                else:
                    # ToDo: Update bool values if decided how to query wiki config
                    bool_value = "true" if value else "false"
                    res += f"|{label}={bool_value}{separator}"
            elif value is not None:
                label = parameter.replace("_", " ")
                res += f"|{label}={value}{separator}"
        return res


class ListOf(SMWPart):
    """
    Provides methods to generate a List of page for a topic
    """

    def __init__(self, wikiRender=None):
        super().__init__("List of", wikiRender)

    @staticmethod
    def get_page_name(topic: Topic):
        return f"List of {topic.plural_name}"


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

    @staticmethod
    def get_page_name(topic: Topic):
        return f"Form:{topic.name}"

    @staticmethod
    def page_form_function(tag, **kwargs):
        """

        Args:
            tag: Type of the form function. e.g.: field, form, info, ...
            **kwargs: parameters of the form function
        Returns:

        """
        return "{{{" + tag + SMW.render_parameters(presence_is_true=True, **kwargs) + "}}}"

    @staticmethod
    def standard_input_tag(input, **kwargs):
        """
        Renders standard input tag
        For more detail see: https://www.mediawiki.org/wiki/Extension:Page_Forms/Defining_forms#'standard_input'_tag
        Args:
            input:
            **kwargs:
        Returns:
        """
        possible_input_tags = ["save", "preview", "save and continue", "changes", "summary", "minor edit", "watch", "cancel"]
        if input not in possible_input_tags:
            tags = ','.join(possible_input_tags)
            raise AttributeError(f"Form standard input \"{input}\" was given but must be one of the following values:{tags}")
        return Form.page_form_function(tag="standard input", **{input:True, **kwargs})

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
    def field(property: Property,regexps={}):
        prop_map = {"input_type":"input_type",
                    "placeholder":"placeholder",
                    "default_value":"default",
                    "values_from":"values_from",
                    "uploadable":"uploadable",
                    "primary_key":"unique"}
        parameters = {}
        for prop in prop_map.keys():
            if prop in property.__dict__ and property.__dict__[prop] is not None:
                if prop == "values_from":
                    # values_from contains data like "concept=Country" so we add an auxiliary property "values from concept" with the value "Country"
                    vals = property.__dict__[prop].split("=")
                    parameters[f"{prop_map[prop]} {vals[0]}" ] = vals[1]
                else:
                    parameters[prop_map[prop]] = property.__dict__[prop]
                if prop == "inputType" and property.__dict__[prop] == "regexp":
                    parameters.update(Form.regexps.get(property.regexp))
        return Form.page_form_function(tag="field", **{property.label:True, **parameters})


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
                 order: str = None):
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
        self.parameters = ["limit", "offset", "format", "searchlabel", "outro", "intro", "default", "headers", "sort", "order"]

    def render(self, oneliner=True):
        """
        Render this Query to the string format of an SMW query
        Args:
            oneliner: If True the query is rendered into one line. Otherwise the query is rendered in a prettier format.

        Returns:

        """
        separator = ""
        if not oneliner:
            separator = "\n"
        query = f"{{{{#{self.mode}:"
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

    def printout(self, property_name, label=None):
        """
        Add a printout statement to the query. Results in querying the given property name.
        Args:
            property_name: Name of the property that should be queried
            label: Label that should be displayed at the result

        Returns:
            Returns the query itself
        """
        self.printout_statements.append(self.PrintoutStatement(property_name, label))
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
