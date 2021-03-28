'''
Created on 2021-03-07

@author: wf
'''

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

    def render_page(self, entity_name, entity_properties, properties):
        """
        Renders the help page for the given entity using the provided properties
        :param entity_name:
        :param entity_properties:
        :param properties:
        :return: the page
        """
        template_template = self.template_env.get_template(self.template)
        page = template_template.render(entity_name=entity_name,
                                        entity_properties=entity_properties,
                                        all_properties=properties)
        return page

    @staticmethod
    def getAll(wikiRender: WikiRender):
        smwPartList = [
            SMWPart("Category"),
            SMWPart("Concept"),
            SMWPart("Form"),
            SMWPart("Template"),
            SMWPart("Help"),
            SMWPart("List of"),
            SMWPart("Properties"),
            SMWPart("PythonCode")
        ]
        smwParts = {}
        for smwPart in smwPartList:
            smwPart.wikiRender = wikiRender
            smwParts[smwPart.part] = smwPart
        return smwParts


class SMW:
    """Provides functions covering basic SMW features"""

    @staticmethod
    def parser_function(function_name: str, **kwargs):
        """
        Renders the given parameters and function name to the corresponding SMW parser function.
        Parameter names containing a whitespace must be written with an underscore instead.
        :param function_name: name of the function
        :param kwargs: parameters of the parser function
        :return:
        """
        return "{{#" + function_name + ":" + SMW.render_parameters(**kwargs) + "}}"

    @staticmethod
    def render_parameters(**kwargs):
        res = ""
        for parameter, value in kwargs.items():
            if isinstance(value, bool):
                label = parameter.replace("_", " ")
                res += f"|{label}"
            elif value is not None:
                label = parameter.replace("_", " ")
                res += f"|{label}={value}"
        return res

class Form:
    """"""

    @staticmethod
    def page_form_function(tag, **kwargs):
        return "{{{" + tag + SMW.render_parameters(**kwargs) + "}}}"

    @staticmethod
    def standard_input_tag(input, **kwargs):
        """

        :param input:
        :return:
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
        :param form: the name of the PF form to be used.
        :return:
        """
        return SMW.parser_function(function_name="forminput", **kwargs)

    @staticmethod
    def formlink(**kwargs):
        """
        Renders a forminput parser function with the given input
        For more details see: https://www.mediawiki.org/wiki/Extension:Page_Forms/Linking_to_forms#Using_#formlink
        :param form: the name of the PF form to be used.
        :return:
        """
        return SMW.parser_function(function_name="formlink", **kwargs)



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
        :param mode: ask for multi page query / show for single page query
        :param mainlabel: title of the first column
        :param limit: maximal number of pages selected
        :param offset: where to start selecting pages
        :param searchlabel: text for continuing the search
        :param outro: text that is appended to the output, if at least some results exist
        :param intro: initial text that prepends the output, if at least some results exist
        :param default: if, for any reason, the query returns no results, this will be printed instead
        :param format: output format  of the query
        :param headers: Show headers (with links), plain headers (just text) or hide them. show is default. Possible values show, hide and, plain.
        :param order: defines how results should be ordered, ascending is the default. Possible values ascending/asc, descending/desc/reverse, random/rand.
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
        :param oneliner: If True the query is rendered into one line. Otherwise the query is rendered in a prettier format.
        :return:
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
        :param property_name: Name of the property that should be queried
        :param label: Label that should be displayed at the result
        :return: Returns the query itself
        """
        self.printout_statements.append(self.PrintoutStatement(property_name, label))
        return self

    def select(self, selector):
        """
        Add page selector to the query
        :param selector:
        :return: Returns the query itself
        """
        self.page_selections.append(selector)
        return self

    def sort_by(self, *properties):
        """
        Set the sort parameter of the query. If already set it overwrites the existing parameter.
        :param properties:
        :return:
        """
        self.sort = ",".join(properties)
        return self

    class PrintoutStatement:
        """Printout statement of a SMW query"""

        def __init__(self, property_name, label=None):
            """
            Init the printout statement
            :param property_name: Name of the property that should be queried
            :param label: Label that should be displayed at the result
            """
            self.property_name = property_name
            self.label = label

        def render(self):
            """
            Render this PrintoutStatement to the string format of an printout statement
            :return:
            """
            label = f"={self.label}" if self.label else ""
            return f"?{self.property_name}{label}"
