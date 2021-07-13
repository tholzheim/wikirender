from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from wikifile.wikiFileManager import WikiFileManager
import os
import wikitextparser as wtp
from mwclient.page import Page
from wikitextparser import Template


class WikiFile:
    '''
    Provides methods to modify, query, update and save files that contain wiki text markup.
    see https://en.wikipedia.org/wiki/Help:Wikitext
    '''

    def __init__(self, name, wikiFileManager:WikiFileManager, wikiText: str = None, debug=False):
        """

        Args:
            name: Name of the file
            path: Path to file location
            wiki_render:
            wikiText: WikiPage content as string. If defined the file content will loaded and this value will be used instead
        """
        self.wikiFileManager=wikiFileManager
        self.pageTitle = self.sanitizePageTitle(name)
        self.wiki_render = wikiFileManager.wikiRender
        self.debug = debug
        if wikiText is None:
            self.wikiText = self.get_wikiText(self.pageTitle, self.wikiFileManager.wikiTextPath)
        else:
            self.wikiText = wtp.parse(wikiText)

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

    def get_wikiText(self, name, path):
        """
        find the wiki file by name and return it as parsed object.
        Args:
            name: Name of the file
            path: Path to the file

        Returns:
            WikiText object
        """
        fname = WikiFile.get_wiki_path(path, name)
        if os.path.isfile(r"{}".format(fname)):
            with open(fname, mode='r') as file:
                page = file.read()
                parsed_page = wtp.parse(page)
                return parsed_page
        return None

    def get_template(self, template_name: str):
        """
        Returns the template
        
        Args:
            template_name(str): the name of the template to extract

        Returns:

        """
        if self.wikiText is None or self.wikiText.templates is None:
            # Wikifile has no templates
            return None
        for template in self.wikiText.templates:
            name = WikiFile.get_template_name(template.name)
            if name == WikiFile.get_template_name(template_name):
                return template
        return None

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
        name = template_name.replace('\n', '')
        name = name.lstrip()
        name = name.rstrip()
        return name

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
                    template.set_arg(key, value)
                else:
                    pass
            else:
                if value is not None:
                    postfix=""
                    if prettify:
                        postfix="\n"
                    template.set_arg(key, value+postfix, preserve_spacing=False)

    def add_template(self, template_name: str, data: dict, overwrite=False, prettify:bool=False):
        """
        Adds the given data as template with the given name to this wikifile.
        If the template is already present only the arguments are updated (the values are only overwritten if overwrite
        is set to True)
        ToDo: Currently unhandled is the behavior if multiple templates with the same name exist
        Args:
            template_name(str): Name of the template the data should be inserted in
            data(dict): Data that should be saved in form of a template
            overwrite(bool): If true existing values are overwritten. Otherwise onl missing values are added. Default: False
            prettify: If true each newly added value will be placed in a new line. Oterwise values are added in the same line. Default is false.

        Returns:
            Nothing
        """
        template = self.get_template(template_name)
        if template is None:
            # create template
            self.wikiText.insert(0, self.wiki_render.render_template(template_name, data))
        else:
            WikiFile.update_arguments(template, data, overwrite, prettify)

    def extract_template(self, name: str):
        """
        Extracts the template data and returns it as dict
        ToDo: Currently unhandled is the behavior if multiple templates with the same name exist

        Args:
            name: name of the template that should be extracted

        Returns:
            Returns template content as dict
        """
        template = self.get_template(name)
        if template is None:
            return None
        res = {}
        for arg in template.arguments:
            value = arg.value.strip()
            if value.endswith("\n"):
                value=value[:-1]
            res[arg.name.strip()] = value
        return res

    def setPage(self, page:Page):
        self.pageRef=page

    def getPage(self)->Page:
        if 'pageRef' in self.__dict__:
            return self.__dict__["pageRef"]

    def getPageTitle(self):
        return self.pageTitle

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

    def __str__(self) -> str:
        return str(self.wikiText)

