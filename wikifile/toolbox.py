from wikifile.wikiFile import WikiFile
from wikifile.smw import SMWPart
from wikifile.metamodel import Property
import json
import logging
import sys
import jinja2
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter


from lodstorage.jsonable import JSONAble, Types


class Toolbox(object):
    """Bundles methods that are required by the commandline tools that this file provides"""

    def __init__(self, argv=None):
        # Setup argument parser
        self.parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
        self.parser.add_argument('-p', '--pages', dest="pages",
                            help="Names of the pages the action should be applied to")
        self.parser.add_argument('--BackupPath', dest="backupPath", help="Path to store/update the wiki entries",
                            required=True)
        self.parser.add_argument('-stdin', dest="stdin", action='store_true',
                            help='Use the input from STD IN using pipes')
        self.parser.add_argument('-ex', '--exclude', dest="exclude_keys",
                            help="List of keys that should be excluded")
        self.parser.add_argument('--debug', dest="debug", action='store_true', default=False, help="Enable debug mode")

    def fromJson(self, listname: str, jsonStr: str, sample: list = None):
        """
        Convert the given string to JSON and convert the values to the corresponding datatype"
        Args:
            listname: name of the list the data is stored in
            jsonStr: data as json string that should be converted
            sample: sample data of the actual data. Used to convert the values to the correct type
        Returns:
            
        """""
        types = Types(listname)
        types.getTypes("data", sample, 1)
        json_parsed = JSONAble()
        json_parsed.fromJson(jsonStr, types)
        return json_parsed.__dict__[listname]

    def update_or_create_templates(self,
                                   data: list,
                                   name_id: str,
                                   template_name: str,
                                   template_env: jinja2.Environment,
                                   backup_path: str,
                                   exclude_keys: list = None,
                                   overwrite=False):
        """
        Iterates over the given data and updates or creates the corresponding wikifile. The parameter wiki_id is used
        as the filename.
        Args:
            data: json data containing the information for the templates
            name_id: Name of the key that contains the page name
            template_name: Name of the template
            template_env:
            backup_path: path to the directory were the wiki files are stored
            exclude_keys: List of keys that is included in the data but should be excluded
            overwrite: If True arguments that are already defined in the template are overwritten by the given data. If False only missing data is added
        Returns:

        """
        for page in data:
            # check if page exists
            if name_id not in page:
                continue
            page_name = page[name_id]
            wiki_render = WikiRender(template_env)
            wiki_file = WikiFile(page_name, backup_path, wiki_render=wiki_render)
            if wiki_file.wikiText is None:
                # create page and store it
                page_content = wiki_render.render_template(template_name, page)
                WikiFile(path=backup_path, name=page_name, wiki_render=wiki_render, wikiText=page_content).save_to_file(
                    overwrite)
            else:
                # update existing template or create new one
                wiki_file.add_template(template_name, page, exclude_keys)
                wiki_file.save_to_file(overwrite=overwrite)

