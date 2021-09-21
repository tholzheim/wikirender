from tabulate import tabulate


class Widget:

    def render(self):
        raise NotImplemented

    def __str__(self):
        return self.render()

class Table(Widget):
    """
    Renders a table in mediawiki markup
    see https://www.mediawiki.org/wiki/Help:Tables
    """
    def __init__(self, tableRecords:list, escapePipe=False):
        self.tableRecords=tableRecords
        self.escapePipe=escapePipe

    def render(self):
        markup=tabulate(self.tableRecords, tablefmt="mediawiki", headers="keys")
        if self.escapePipe:
            markup=markup.replace("|", "{{!}}")
        return markup


class Itemize(Widget):
    '''
    Renders unordered list
    see https://www.mediawiki.org/wiki/Help:Lists
    '''

    def __init__(self, records:list, listChar:str="*", level:int=1):
        self.records=records
        self.listChar=listChar
        self.level=level

    def render(self):
        markup=""
        for record in self.records:
            if isinstance(record, Widget):
                record = record.render()
            if isinstance(record, str):
                markup+=f"{self.listChar*self.level}{record}\n"
            elif isinstance(record, list):
                markup+=Itemize(record,listChar=self.listChar, level=self.level+1).render()
        return markup

class Enumerate(Itemize):
    '''
    Renders ordered list
    see https://www.mediawiki.org/wiki/Help:Lists
    '''
    def __init__(self, records: list):
        super().__init__(records, listChar="#")

class Link(Widget):
    '''
    Renders external link
    See https://www.mediawiki.org/wiki/Help:Links
    '''

    def __init__(self, url:str, linkText:str):
        self.url=url
        self.linkText=linkText

    def render(self):
        markup=f"[{self.url} {self.linkText}]"
        return markup

class PageLink(Widget):
    '''
    Renders page link
    See https://www.mediawiki.org/wiki/Help:Links
    '''

    def __init__(self, pageTitle:str, linkText:str=None):
        self.pageTitle=pageTitle
        self.linkText=linkText

    def render(self):
        linkText=f"|{self.linkText}" if self.linkText else ""
        markup=f"[[{self.pageTitle}{linkText}]]"
        return markup

class MagicWord(Widget):
    def __init__(self, magicword:str):
        self.value=magicword

    def render(self):
        markup="{{%s}}" % str(self.value)
        return markup
MagicWord.PAGENAME=MagicWord("PAGENAME")

class Template(Widget):
    """
    Renders template in wiki markup
    """

    def __init__(self, templateName:str, parameter:dict):
        self.templateName=templateName
        self.parameter=parameter

    def render(self, oneliner:bool=False):
        joinStr= "\n|" if not oneliner else "|"
        values=""
        if self.parameter:
            values=joinStr+joinStr.join([f'{key}={value}' for key, value in self.parameter.items()])
        markup=f"{{{{{self.templateName}{values}}}}}"
        return markup

class WikiSon(Template):
    """
    Renders a WikiSon object
    """

    def __init__(self, topicName, properties:dict):
        super(WikiSon, self).__init__(topicName, properties)

class ParserFunction(Widget):
    """
    Renders a parser function
    see https://www.mediawiki.org/wiki/Help:Extension:ParserFunctions
    """

    def __init__(self, functionName:str, *arguments):
        self.functionName=functionName
        self.arguments=arguments

    def render(self, oneliner:bool=False):
        joinStr = "\n|" if not oneliner else "|"
        argumentsMarkup=""
        if self.arguments:
            if "=" in str(self.arguments[0]):
                argumentsMarkup+=joinStr
            argumentsMarkup+=joinStr.join(map(str,self.arguments))
        postFix='' if oneliner else '\n'
        markup=f"{{{{#{self.functionName}:{argumentsMarkup}{ postFix }}}}}"
        return markup

class SubObject(ParserFunction):
    """
    Renders a subobject by setting the given values as properties of a subobject
    see https://www.semantic-mediawiki.org/wiki/Help:Adding_subobjects
    """

    def __init__(self, name, **properties):
        super().__init__("subobject", name, *[f"{key}={value}" for key, value in properties.items()])

class SetProperties(ParserFunction):
    """
    Renders the property set parser function
    see https://www.semantic-mediawiki.org/wiki/Help:Setting_values
    """

    def __init__(self,**properties):
        super().__init__("set", *[f"{key}={value}" for key, value in properties.items()])


class TemplateParam(Widget):
    """Renders a template parameter"""

    def __init__(self, paramName:str, setDefaultValue:bool=True, defaultValue=None):
        """

        Args:
            paramName(str): name of the parameter. For positional parameters use numbers
            setDefaultValue(bool): If true the parameter will be rendered with a set default value. If the default value is not set empty string is used as default
            defaultValue: default value for the parameter
        """
        self.paramName=paramName
        self.setDefaultValue=setDefaultValue
        self.defaultValue=defaultValue

    def render(self):
        defaultValue=""
        if self.setDefaultValue:
            defaultValue=f"|{defaultValue}"
        markup=f"{{{{{{{self.paramName}{defaultValue}}}}}}}"
        return markup

class SwitchFunction(ParserFunction):
    """
    Renders a switch parser function
    """

    def __init__(self, compare:str, **cases):
        """

        Args:
            compare: string to compare the cases to
            **cases: different cases and their result
        """
        super().__init__("switch", compare, *[f"{key}={value}" if value is not None else key for key, value in cases.items()])