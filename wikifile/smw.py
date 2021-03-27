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


class Form:
    """"""

    @staticmethod
    def standard_input_tag(input, label="", css_class="", style=""):
        """

        :param input:
        :param label:
        :param css_class:
        :param style:
        :return:
        """
        possible_input_tags = ["save", "preview", "save and continue", "changes", "summary", "minor edit", "watch", "cancel"]
        if input not in possible_input_tags:
            tags = ','.join(possible_input_tags)
            raise AttributeError(f"Form standard input \"{input}\" was given but must be one of the following values:{tags}")
        input_tag = "{{{standard input|" + input
        if label:
            input_tag += "|label=" + label
        if css_class:
            input_tag += "|class=" + css_class
        if style:
            input_tag += "|style=" + style
        return input_tag + "}}}"

    @staticmethod
    def forminput(form: str,
                  size=None,
                  default_value=None,
                  button_text=None,
                  query_string=None,
                  autocomplete_on_category=None,
                  autocomplete_on_namespace=None,
                  placeholder=None,
                  namespace_selector=None,
                  popup: bool = False,
                  no_autofocus: bool = False,
                  returnto=None,
                  reload: bool = False):
        """
        Renders a forminput parser function with the given input
        For more details see: https://www.mediawiki.org/wiki/Extension:Page_Forms/Linking_to_forms#Using_#forminput
        :param form: the name of the PF form to be used.
        :param size: the size of the text input
        :param default_value: the starting value of the input
        :param button_text: the text that will appear on the "submit" button (default is "Create or edit page").
        :param query_string: used to pass information to the form; this information generally takes the form of templateName[fieldName]=value.
        :param autocomplete_on_category: adds autocompletion to the input, using the names of all pages in a specific category.
        :param autocomplete_on_namespace: adds autocompletion to the input, using the names of all pages in a specific namespace
        :param placeholder: text that appears in the form input before the user types anything.
        :param namespace_selector: add dropdown list before the input field to allow to select a namespace
        :param popup: opens the form in a popup window.
        :param no_autofocus:by default; the form input gets autofocus
        :param returnto: the name of a page that the user will be sent to after submitting the form, instead of simply going to the saved page.
        :param reload: if "popup" or "returnto" are specified, causes the page that the user ends up on after submitting the form to get reloaded with 'action=purge'.
        :return:
        """
        value_parameter = ["form", "size", "default_value", "button_text", "query_string", "autocomplete_on_category",
                          "autocomplete_on_namespace", "placeholder", "namespace_selector", "returnto"]
        bool_parameter = ["popup", "no_autofocus", "reload"]
        forminput = "{{#forminput:"
        for parameter, value in locals().items():
            if parameter in value_parameter:
                if value is not None:
                    label = parameter.replace("_", " ")
                    forminput += f"|{label}={value}"
            elif parameter in bool_parameter:
                if value:
                    label = parameter.replace("_", " ")
                    forminput += f"|{label}"
        return forminput + "}}"



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
