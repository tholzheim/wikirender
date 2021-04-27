import os
import wikitextparser as wtp
from wikitextparser import Template


class WikiFile:
    '''
    Provides methods to modify, query, update and save wiki files.
    '''

    def __init__(self, name, path, wiki_render, wikiText: str = None, debug=False):
        """

        Args:
            name: Name of the file
            path: Path to file location
            wiki_render:
            wikiText: WikiPage contend as string. If defined the file content will loaded and this value will be used instead
        """
        self.file_name = name
        self.file_path = path
        self.debug = debug
        if wikiText is None:
            self.wikiText = self.get_wikiText(self.file_name, self.file_path)
        else:
            self.wikiText = wtp.parse(wikiText)
        self.wiki_render = wiki_render

    def save_to_file(self, overwrite=False):
        """
        Save the given data in a file.
        Args:
            overwrite: If True existing files will be over written and if the path does not exist the missing folder will be created. Otherwise, only missing files will be saved.
        Returns:

        """
        wiki_file_path = WikiFile.get_wiki_path(self.file_path, self.file_name)
        mode = "w"
        if overwrite:
            mode = 'w'
            os.makedirs(os.path.dirname(wiki_file_path), exist_ok=True)
        else:
            if os.path.isfile(wiki_file_path):
                # file already exists
                if self.debug:
                    print(f"File {wiki_file_path} exists \t-> Generated page not saved. To save also existing pages use -f to overwrite them.", )
                    return
        with open(wiki_file_path, mode=mode) as f:
            f.write(str(self.wikiText))
        if self.debug:
            print(f"{self.file_name} saved to {wiki_file_path}")

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
                if value is not None:
                    template.set_arg(key, value)

    def add_template(self, template_name: str, data: dict, overwrite=False):
        template = self.get_template(template_name)
        if template is None:
            # create template
            self.wikiText.insert(0, self.wiki_render.render_template(template_name, data))
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
