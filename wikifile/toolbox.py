import json
import logging
import sys
import jinja2
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from wikifile.wikiExtract import extract_templates
from wikifile.wikiFile import WikiFile, get_wiki_path
from wikifile.wikiRender import WikiRender, Topic


def save_to_file(path, filename, data, overwrite=False):
    """Save the given data in a file"""
    mode = 'a'
    if overwrite:
        mode = 'w'
    with open(get_wiki_path(path, filename), mode=mode) as f:
        f.write(data)


def update_or_create_templates(data: list,
                               name_id: str,
                               template_name: str,
                               template_env: jinja2.Environment,
                               backup_path: str,
                               exclude_keys: list = None,
                               overwrite=False):
    """
    :param exclude_keys: List of keys that is included in the data but should be excluded
    :param template_name: Name of the template
    :param data: json data containing the information for the templates
    :param name_id: Name of the key that contains the page name
    :param template_env:
    :param backup_path: path to the directory were the wiki files are stored
    :param overwrite: If True arguments that are already defined in the template are overwritten by the given data. If False only missing data is added
    :return:
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
            save_to_file(backup_path, page_name, page_content)
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
    templateEnv=WikiRender.getTemplateEnv()
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
            properties = {}
            with open(args.properties_file) as json_file:
                properties = json.load(json_file).get('data')
            topics = {}
            with open(args.topics_file) as json_file:
                topics = json.load(json_file).get('data')
            for topic in topics:
                topic_obj = Topic(topic)
                # Generate and save the entity pages
                # Template
                save_to_file(args.backupPath,
                             f"Template:{topic_obj.name}",
                             wiki_render.render_template_page(topic_obj.name, topic, properties),
                             args.overwrite)
                # Concept
                save_to_file(args.backupPath,
                             f"Concept:{topic_obj.name}",
                             wiki_render.render_concept_page(topic_obj.name, topic, properties),
                             args.overwrite)
                # Category
                save_to_file(args.backupPath,
                             f"Category:{topic_obj.name}",
                             wiki_render.render_category_page(topic_obj.name, topic, properties),
                             args.overwrite)
                # Help
                save_to_file(args.backupPath,
                             f"Help:{topic_obj.name}",
                             wiki_render.render_help_page(topic_obj.name, topic, properties),
                             args.overwrite)
                # List of
                save_to_file(args.backupPath,
                             f"List of {topic_obj.plural_name}",
                             wiki_render.render_list_of_page(topic_obj.name, topic, properties),
                             args.overwrite)
                # Form
                save_to_file(args.backupPath,
                             f"Form:{topic_obj.name}",
                             wiki_render.render_form_page(topic_obj.name, topic, properties),
                             args.overwrite)
        if args.template == "Event":
            if 'data' in data:
                events = data['data']
            else:
                pass
            update_or_create_templates(data=events,
                                       name_id=args.page_name_id,
                                       template_name=args.template,
                                       template_env=templateEnv,
                                       backup_path=args.backupPath,
                                       overwrite=args.overwrite,
                                       exclude_keys=args.exclude_keys)
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

        res_templates = extrat_templates(args.template, stdIn=args.stdin, file_list=args.file_list,
                                         page_titles=args.pages, backup_path=args.backupPath,
                                         add_file_name=args.file_name_id)
        print(res_templates)


    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        print(e)


if __name__ == "__main__":
    sys.argv.append("-m=generate_entity_pages")
    sys.argv.append("--properties=")
    sys.argv.append("--topics=")
    sys.argv.append("--BackupPath=")
    main_render(sys.argv[1:])
    pass