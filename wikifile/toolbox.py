import json
import logging
import sys
import jinja2
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from wikifile.metamodel import Property
from wikifile.wikiExtract import WikiExtract
from wikifile.wikiFile import WikiFile
from wikifile.wikiRender import WikiRender, Topic
from wikifile.smw import SMWPart
from lodstorage.jsonable import JSONAble, Types


class Toolbox:
    """Bundles methods that are required by the commandline tools that this file provides"""

    def fromJson(self, listname: str, jsonStr: str, sample: list = None):
        """
        Convert the given string to JSON and convert the values to the corresponding datatype"
        Args:
            listname: name of the list the data is stored in
            jsonStr: data as json string that should be converted
            sample: sample data of the actual data. Used to convert the values to the vorrect type
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


def main_render(argv=None):
    # Modes of operation
    UPDATE_TEMPLATES_MODE = "update_templates"
    CREATE_FILE_MODE = "create"
    GENERATE_ENTITY_PAGES = "generate_entity_pages"
    modes = [UPDATE_TEMPLATES_MODE, CREATE_FILE_MODE, GENERATE_ENTITY_PAGES]
    templateEnv = WikiRender.getTemplateEnv()
    wiki_render = WikiRender(templateEnv)
    try:
        # Setup argument parser
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-m", "--mode", dest="mode",
                            help="Select a mode.\n\tupdate_templates: updates the wikifiles at the provided location with the provided data\n\tcreate: creates a wikifile with the given data.",
                            required=True)
        parser.add_argument("-t", "--template", dest="template",
                            help="Select a template in which the data is being rendered")
        parser.add_argument("-id", "--page_name_id", dest="page_name_id",
                            help="Select a template in which the data is being rendered")
        parser.add_argument('-d', '--data', dest="data_input", help="Input data which should be rendered")
        parser.add_argument('--properties', dest="properties_file", help="Json file containing properties")
        parser.add_argument('--topics', dest="topics_file", help="Json file containing topics")
        parser.add_argument('--BackupPath', dest="backupPath", help="Path to store/update the wiki entries",
                            required=True)
        parser.add_argument('-stdin', dest="stdin", action='store_true', help='Use the input from STD IN using pipes')
        parser.add_argument('-ex', '--exclude', dest="exclude_keys",
                            help="List of keys that should be excluded")
        parser.add_argument('-f', dest="overwrite", action='store_true', default=False,
                            help='If true template arguments will be overwritten with the given data if present')
        # ToDo: Add parameter to allow custom templates that can load the macros from here

        # Process arguments
        args = parser.parse_args(argv)
        if args.mode not in modes:
            raise Exception(f"Please select of of the operation modes: {modes}")
        data = {}
        if args.data_input:
            data = json.loads(args.data_input)
        elif args.stdin:
            data = json.load(sys.stdin)
        else:
            pass
        if args.mode == GENERATE_ENTITY_PAGES:
            # Check if necessary parameters are set
            if not args.properties_file or not args.topics_file:
                raise Exception("The parameters --properties and --topics must be defined for this mode")
            # TODO:
            # use fromJson
            properties = []
            with open(args.properties_file) as json_file:
                properties = [Property(x) for x in Toolbox().fromJson("data", json_file.read(), Property.get_samples())]
            topics = []
            with open(args.topics_file) as json_file:
                topics = [Topic(x) for x in Toolbox().fromJson("data", json_file.read(), Topic.get_samples())]
            for topic in topics:
                # Generate and save the entity pages
                # Template
                # TODO:
                for part, smwPart in SMWPart.getAll(wiki_render).items():
                    page = smwPart.render_page(topic, properties)
                    WikiFile(smwPart.get_page_name(topic), args.backupPath, wiki_render=wiki_render,
                             wikiText=page).save_to_file(args.overwrite)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        print(e)


def main_extract(argv=None):
    try:
        # Setup argument parser
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-t", "--template", dest="template",
                            help="Select a template in which the data is being rendered", required=True)
        parser.add_argument("-id", "--file_name_id", dest="file_name_id",
                            help="Name of the key in which the file name is stored.")
        parser.add_argument('-p', '--pages', dest="pages",
                            help="Input data which should be rendered. If none given whole folder will be used.")
        parser.add_argument('--BackupPath', dest="backupPath", help="Path to the wikifiles", required=True)
        parser.add_argument('-stdin', dest="stdin", action='store_true', help='Use the input from STD IN using pipes')
        parser.add_argument('--debug', dest="debug", action='store_true', default=False, help="Path to the wikifiles")
        parser.add_argument("--listFile", dest="file_list",
                            help="List of pages form which the data should be extracted", required=False)

        # Process arguments
        args = parser.parse_args(argv)
        if args.debug:
            logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        else:
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)

        file_parameters = [args.stdin, args.pages, args.file_list]
        if len(file_parameters) - (file_parameters.count(None) + file_parameters.count(False)) > 1:
            logging.error(
                "Multiple file selection options were used. Please use only one or none to select all files in the backup folder.")
            raise Exception("Invalid parameters")

        res_templates = WikiExtract.extract_templates(args.template,
                                                     stdIn=args.stdin,
                                                     file_list=args.file_list,
                                                     page_titles=args.pages,
                                                     backup_path=args.backupPath,
                                                     add_file_name=args.file_name_id)
        print(res_templates)


    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        print(e)


if __name__ == "__main__":
    templateEnv = WikiRender.getTemplateEnv(script_dir="..")
    wiki_render = WikiRender(templateEnv)
    properties = []
    with open("/home/holzheim/wikibackup/rq_properties2.json") as json_file:
        properties = [Property(x) for x in Toolbox().fromJson("data", json_file.read(), Property.get_samples())]
    topics = []
    with open("/home/holzheim/wikibackup/rq_topics2.json") as json_file:
        topics = [Topic(x) for x in Toolbox().fromJson("data", json_file.read(), Topic.get_samples())]
    for topic in topics:
        # Generate and save the entity pages
        # Template
        # TODO:
        for part, smwPart in SMWPart.getAll(wiki_render).items():
            page = smwPart.render_page(topic, properties)
            WikiFile(smwPart.get_page_name(topic), "/home/holzheim/wikibackup/rq_test", wiki_render=wiki_render,
                     wikiText=page).save_to_file(True)
    pass
