import os
import wikitextparser as wtp
from wikitextparser import Template
from wikifile.wikiRender import WikiRender


def get_wiki_path(path: str, name: str):
    return f"{path}/{name}.wiki"


class WikiFile:

    def __init__(self, name, path, wiki_render: WikiRender):
        """

        :param name: Name of the file
        :param path: Path to file location
        """
        self.file_name = name
        self.file_path = path
        self.wikiText = self.get_wikiText(self.file_name, self.file_path)
        self.wiki_render = wiki_render

    def save_to_file(self, overwrite=False):
        """Save the given data in a file"""
        mode = 'a'
        if overwrite:
            mode = 'w'
        with open(WIKI_FILE_PATH(self.file_path, self.file_name), mode=mode) as f:
            f.write(str(self.wikiText))

    def get_wikiText(self, name, path):
        """
        find the wiki file by name and return it as parsed object.

        :return None if the file is not found
        """
        fname = WIKI_FILE_PATH(path, name)
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
        :param name: name of the template that should be extracted
        :return: Returns template content as dict
        """
        template = self.get_template(name)
        if template is None:
            return None
        res = {}
        for arg in template.arguments:
            value = arg.value if not arg.value.endswith("\n") else arg.value[:-1]
            res[arg.name] = value
        return res

