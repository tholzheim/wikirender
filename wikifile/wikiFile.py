from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from wikifile.wikiFileManager import WikiFileManager
import os
import warnings
import wikitextparser as wtp
from mwclient.page import Page
from wikitextparser import Template

class WikiFile:
    '''
    Provides methods to modify, query, update and save files that contain wiki text markup.
    see https://en.wikipedia.org/wiki/Help:Wikitext
    '''

    def __init__(self, name, wikiFileManager:WikiFileManager=None, wikiText: str = None, debug=False):
        """

        Args:
            name: page title of the wikiText file
            wikiFileManager: WikiFileManager providing context information for this WikiFile
            wikiText: WikiPage content as string. If None try to init the wikiText from source location
        """
        self.wikiFileManager=wikiFileManager
        self.pageTitle = self.sanitizePageTitle(name)
        if wikiFileManager:
            self.wiki_render = wikiFileManager.wikiRender
        self.debug = debug
        self._wikiText=wikiText
        if wikiText is None:
            self._wikiText=self.get_wikiText_from_source()
        self._parsedWikiText=None

    @property
    def wikiText(self):
        if self._parsedWikiText is None:
            return self._wikiText
        else:
            return str(self.parsedWikiText)

    @wikiText.setter
    def wikiText(self, wikiText:str):
        self._wikiText=wikiText
        if self._parsedWikiText is not None:
            # update parsed wikiText
            self._parsedWikiText=wtp.parse(wikiText)

    @property
    def parsedWikiText(self):
        if self._parsedWikiText is None and self._wikiText is not None:
            self._parsedWikiText=wtp.parse(self._wikiText)
        return self._parsedWikiText

    @parsedWikiText.setter
    def parsedWikiText(self, parsedWikiText: wtp.WikiText):
        self._parsedWikiText=parsedWikiText

    def sanitizePageTitle(self, name:str):
        """
        Cleans the given name to a normalized page title by removing the file suffix and removing the location path
        Args:
            name: Name identifying the

        Returns:

        """
        if self.wikiFileManager is not None:
            suffix='.wiki'
            # if completely migrated to python 3.9 exchange with removesuffix()
            if name.endswith(suffix):
                name=name[:-len(suffix)]
            # if completely migrated to python 3.9 exchange with removeprefix()
            prefix=f"{self.wikiFileManager.wikiTextPath}/"
            if name.startswith(prefix):
                name=name[len(prefix):]
        return name



    def save_to_file(self, overwrite=False):
        """
        Save the given data in a file.
        
        Args:
            overwrite(bool): If True existing files will be over written and if the path does not exist the missing folder will be created. Otherwise, only missing files will be saved.
  
        """
        WikiFile.write_to_file(self.file_path, self.pageTitle, str(self), overwrite=overwrite)

    @staticmethod
    def write_to_file(path:str, pageTitle,content:str,overwrite:bool=False, debug:bool=False):
        """

        Args:
            path:
            content:
            overwrite:
            debug:

        Returns:

        """
        wiki_file_path = WikiFile.get_wiki_path(path, pageTitle)
        mode = "w"
        if overwrite:
            mode = 'w'
            os.makedirs(os.path.dirname(wiki_file_path), exist_ok=True)
        else:
            if os.path.isfile(wiki_file_path):
                # file already exists
                if debug:
                    print(
                        f"File {wiki_file_path} exists \t-> Generated page not saved. To save also existing pages use -f to overwrite them.", )
                    return
        with open(wiki_file_path, mode=mode) as f:
            f.write(str(content))
        if debug:
            print(f"{pageTitle} saved to {path}")

    def get_wikiText_from_source(self):
        """
        find the wiki file by name and return it as parsed object.
        Args:
            name: Name of the file
            path: Path to the file

        Returns:
            WikiText object
        """
        fname = WikiFile.get_wiki_path(self.wikiFileManager.wikiTextPath, self.pageTitle)
        if os.path.isfile(fname):
            with open(fname, mode='r') as file:
                page = file.read()
            return page
        return None

    def get_template(self, template_name: str):
        """
        Returns the template
        ToDo: Extend functionality to support multiple template occurences
        Args:
            template_name(str): the name of the template to extract

        Returns:

        """
        warnings.warn("get_template is deprecated as it only supports the first template occurrence. Please switch to getTemplatesByName",
                      DeprecationWarning)
        if self.parsedWikiText is None or self.parsedWikiText.templates is None:
            # Wikifile has no templates
            return None
        targetTemplateName=WikiFile.get_template_name(template_name)
        for template in self.parsedWikiText.templates:
            name = WikiFile.get_template_name(template.name)
            if name == targetTemplateName:
                return template
        return None

    def getTemplatesByName(self, _templateName:str, match:dict={}) -> list:
        """
        Returns the templates matching the given name and if additional matches are defined the values of the template
        also have to match these
        Args:
            _templateName: name of the template
            match(dict): Additional matching criteria

        Returns:
            list of templates with the given name matching the given criteria
        """
        if self.parsedWikiText is None or self.parsedWikiText.templates is None:
            # Wikifile has no templates
            return []
        targetTemplateName=WikiFile.get_template_name(_templateName)
        matchingTemplates=[]
        for template in self.parsedWikiText.templates:
            name = WikiFile.get_template_name(template.name)
            if name == targetTemplateName:
                matches=True
                for key, value in match.items():
                    if not template.has_arg(key, value):
                        matches=False
                if matches:
                    matchingTemplates.append(template)
        return matchingTemplates

    def extractTemplatesByName(self, _templateName: str, match:dict={}) -> list:
        """
        Extracts and returns the template values
        Args:
            _templateName: name of the template
            match(dict): Additional matching criteria

        Returns:
            list of dicts containing the parameter and their values of the corresponding template
        """
        templates=self.getTemplatesByName(_templateName, match)
        res=[]
        if templates:
            for template in templates:
                if not isinstance(template, Template):
                    continue
                templateValues={arg.name.rstrip().lstrip():arg.value.rstrip().lstrip() for arg in template.arguments}
                res.append(templateValues)
        return res

    def addTemplate(self, template_name: str, data: dict, prettify:bool=False):
        """
        Adds the given data as template with the given name to this wikifile.
        The data is added as new template object to the wikifile.
        Args:
            template_name(str): Name of the template the data should be inserted in
            data(dict): Data that should be saved in form of a template
            prettify: If true each newly added value will be placed in a new line. Otherwise values are added in the same line. Default is false.

        Returns:
            Nothing
        """
        templateMarkup=self.wiki_render.render_template(template_name, data)
        template=Template(templateMarkup)
        self.wikiText=f"{self.wikiText}\n{template}"

    def updateTemplate(self, template_name: str, args:dict, overwrite=False, updateAll:bool=False, prettify:bool=False, match:dict={}):
        """
        Updates the given template the values from the given dict args.
        If force is set to True existing values will be overwritten.
        Args:
            template_name(str): name of the template that should be updated
            args(dict): Dict containing the arguments that should be set. key=argument name, value=argument value
            overwrite(bool): If True existing values will be overwritten
            prettify(bool): If True new values will be added into a new line
            updateAll(bool): If True all matching attributes are updated. Otherwise only one template is updated if matched multiple an error is raised.
            match(dict): matching criteria for the template

        Returns:
            Nothing
        """
        matchingTemplates=self.getTemplatesByName(template_name, match=match)
        if matchingTemplates:
            if len(matchingTemplates)>1 and not updateAll:
                warnings.warn("More than one template were matched. Either improve the matching criteria or enable updateAll", UserWarning)
                pass
            else:
                for template in matchingTemplates:
                    WikiFile.update_arguments(template, args, overwrite, prettify)
        else:
            self.addTemplate(template_name, args)

    @staticmethod
    def get_template_name(template_name: str):
        """
        Removes the whitespace around the template name and the line break if present.
        Example: " Event \n" -> "Event"

        Args:
            template_name: raw template name that should be normalized

        Returns:
            normalized template name.
        """
        if isinstance(template_name, str):
            return template_name.rstrip().lstrip()
        else:
            return template_name

    def update_template(self, template_name: str, args:dict, overwrite=False, prettify:bool=False):
        """
        Updates the given template the values from the given dict args.
        If force is set to True existing values will be overwritten.
        ToDo: Currently unhandled is the behavior if multiple templates with the same name exist
        Args:
            template_name(str): name of the template that should be updated
            args(dict): Dict containing the arguments that should be set. key=argument name, value=argument value
            overwrite(bool): If True existing values will be overwritten
            prettify(bool): If True new values will be added into a new line

        Returns:
            Nothing
        """
        warnings.warn("update_template is deprecated as it only supports the first template occurrence", DeprecationWarning)
        template = self.get_template(template_name)
        self.update_arguments(template, args, overwrite, prettify)

    @staticmethod
    def update_arguments(template: Template, args:dict, overwrite=False, prettify:bool=False):
        """
        Updates the arguments of the given template with the values of the given dict (args)

        Args:
            template: Template that should be updated
            args(dict): Dict containing the arguments that should be set. key=argument name, value=argument value
            overwrite(bool): If True existing values will be overwritten
            prettify(bool): If True new values will be added into a new line

        Returns:
            Nothing
        """
        for key, value in args.items():
            if template.has_arg(key):
                # update argument
                if overwrite:
                    template.del_arg(key)
                    template.set_arg(key, str(value))
                else:
                    pass
            else:
                if value is not None:
                    postfix=""
                    if prettify:
                        postfix="\n"
                    template.set_arg(key, str(value)+postfix, preserve_spacing=False)

    def add_template(self, template_name: str, data: dict, overwrite=False, prettify:bool=False):
        """
        Adds the given data as template with the given name to this wikifile.
        If the template is already present only the arguments are updated (the values are only overwritten if overwrite
        is set to True)
        ToDo: Currently unhandled is the behavior if multiple templates with the same name exist
        Args:
            template_name(str): Name of the template the data should be inserted in
            data(dict): Data that should be saved in form of a template
            overwrite(bool): If true existing values are overwritten. Otherwise only missing values are added. Default: False
            prettify: If true each newly added value will be placed in a new line. Otherwise values are added in the same line. Default is false.

        Returns:
            Nothing
        """
        warnings.warn("add_template is deprecated as it only supports the first template occurrence", DeprecationWarning)
        template = self.get_template(template_name)
        if template is None:
            # create template
            self.parsedWikiText.insert(0, self.wiki_render.render_template(template_name, data))
        else:
            WikiFile.update_arguments(template, data, overwrite, prettify)

    def extractTemplate(self, templateName, match:dict={}) -> list:
        """
        Extracts the template data and returns it as dict

        Args:
            name: name of the template that should be extracted
            match(dict):

        Returns:
            Returns template content as dict and a list if multiple instances of the template are found
        """
        templates=self.getTemplatesByName(templateName, match=match)
        lod=[]
        for template in templates:
            if template is None:
                continue
            records = {}
            for arg in template.arguments:
                value = arg.value.strip()
                if value.endswith("\n"):
                    value = value[:-1]
                records[arg.name.strip()] = value
            if records:
                lod.append(records)
        return lod


    def extract_template(self, name: str):
        """
        Extracts the template data and returns it as dict
        ToDo: Currently unhandled is the behavior if multiple templates with the same name exist

        Args:
            name: name of the template that should be extracted

        Returns:
            Returns template content as dict
        """
        warnings.warn("extract_template is deprecated as it only supports the first template occurrence. Please use extractTemplate instead.",
                      DeprecationWarning)
        templates=self.extractTemplate(name)
        if templates:
            return templates[0]
        return None

    def setPage(self, page:Page):
        self.pageRef=page

    def getPage(self)->Page:
        if 'pageRef' in self.__dict__:
            return self.__dict__["pageRef"]

    def getPageTitle(self):
        return self.pageTitle

    def pushToWiki(self, msg:str=None):
        """
        Pushes the wikiMarkup/WikiText of this object to the target wiki of the wikiFileManager on the page
        corresponding to the pageTitle of the object.

        Args:
            msg(str): Summary of the update (shown as comment in the history of the page)
        """
        page = self.wikiFileManager.wikiPush.toWiki.getPage(self.getPageTitle())
        page.edit(self.wikiText, msg)

    @staticmethod
    def get_wiki_path(path: str, name: str):
        """

        Args:
            path: path the file is located
            name: name of the page also known as page title

        Returns:
            path to the wikitext file based on given path and name
        """
        wikiPath=f"{name}.wiki"
        if path is not None:
            wikiPath=f"{path}/{wikiPath}"
        return wikiPath

    @property
    def file_name(self):
        return self.get_wiki_path(self.wikiFileManager.targetPath, self.pageTitle)

    @property
    def file_path(self):
        return self.wikiFileManager.targetPath

    def __str__(self) -> str:
        return self.wikiText

