import os
import wikitextparser as wtp
from wikitextparser import Template
from wikifile.wikiRender import WikiRender


class WikiFile:
    '''
    Provides methods to modify, query, update and save wiki files.
    '''

    def __init__(self, name, path, wiki_render: WikiRender, wikiText: str = None):
        """

        Args:
            name: Name of the file
            path: Path to file location
            wiki_render:
            wikiText: WikiPage contend as string. If defined the file content will loaded and this value will be used instead
        """
        self.file_name = name
        self.file_path = path
        if wikiText is None:
            self.wikiText = self.get_wikiText(self.file_name, self.file_path)
        else:
            self.wikiText = wtp.parse(wikiText)
        self.wiki_render = wiki_render

    def save_to_file(self, overwrite=False):
        """Save the given data in a file"""
        mode = 'a'
        if overwrite:
            mode = 'w'
        with open(WikiFile.get_wiki_path(self.file_path, self.file_name), mode=mode) as f:
            f.write(str(self.wikiText))

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
        if os.path.isfile(fname):
            with open(fname, mode='r') as file:
                page = file.read()
                parsed_page = wtp.parse(page)
                return parsed_page
        return None

    def get_template(self, template_name: str):
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
        name = template_name.replace('\n', '')
        name = name.lstrip()
        name = name.rstrip()
        return name

    def update_template(self, template_name: str, args, force=False):
        template = self.get_template(template_name)
        for key, value in args.items():
            if template.has_arg(key):
                # update argument
                if force:
                    template.del_arg(key)
                    template.set_arg(key, value)
                else:
                    pass
            else:
                template.set_arg(key, value)

    @staticmethod
    def update_arguments(template: Template, args, overwrite=False):
        for key, value in args.items():
            if template.has_arg(key):
                # update argument
                if overwrite:
                    template.del_arg(key)
                    template.set_arg(key, value)
                else:
                    pass
            else:
                template.set_arg(key, value)

    def add_template(self, template_name: str, data: dict, exclude_keys: list, overwrite=False):
        template = self.get_template(template_name)
        if template is None:
            # create template
            self.wikiText.insert(0, self.wiki_render.render_template(template_name, data, exclude_keys))
        else:
            WikiFile.update_arguments(template, data, overwrite)

    def extract_template(self, name: str):
        """
        Extracts the template data and returns it as dict
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
            value = arg.value if not arg.value.endswith("\n") else arg.value[:-1]
            res[arg.name] = value
        return res

    @staticmethod
    def get_wiki_path(path: str, name: str):
        return f"{path}/{name}.wiki"
