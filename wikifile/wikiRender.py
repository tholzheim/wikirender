import os

import wikifile
from wikifile.wikiFile import WikiFile
from wikifile.metamodel import Context, Topic, UML, Property, MetaModelElement
from wikifile.smw import SMWPart, SMW, Form, ListOf, Query
import json
import sys
import jinja2
from distutils.sysconfig import get_python_lib
from wikifile.cmdline import CmdLineAble


class WikiRender(CmdLineAble):
    """
    Provides functions to render json data to wiki files
    """

    def __init__(self, template_env=None, debug=False):
        ''' constructor
        '''
        self.debug=debug  # debug state before args.debug is available
        super(WikiRender, self).__init__()
        if template_env is None:
            template_env = WikiRender.getTemplateEnv()
        self.template_env = template_env

    def maininstance(self, argv=None):
        if argv is None:
            argv = sys.argv
        
        # Modes of operation
        UPDATE_TEMPLATES_MODE = "update_templates"
        CREATE_FILE_MODE = "create"
        GENERATE_ENTITY_PAGES = "generate_entity_pages"
        modes = [UPDATE_TEMPLATES_MODE, CREATE_FILE_MODE, GENERATE_ENTITY_PAGES]
       
        # Setup argument parser
        self.getParser()
        try:
            # Process arguments
            args = self.parser.parse_args(argv)
            self.debug=args.debug
            if args.mode not in modes:
                raise Exception(f"Please select of of the operation modes: {modes}")
            if args.mode == GENERATE_ENTITY_PAGES:
                # Check if necessary parameters are set
                if not args.properties_file or not args.topic_file:
                    raise Exception("The parameters --properties and --topics must be defined for this mode")
                if args.templates_folder:
                    # update templateEnv
                    self.template_env = self.getTemplateEnv(additional_loader=args.template_folder)
                properties_json = ""
                print(1)
                with open(args.properties_file) as json_file:
                    properties_json = json_file.read()
                topic_json = ""
                with open(args.topic_file) as json_file:
                    topic_json = json_file.read()
                topic = Topic.from_wiki_json(topic_json=topic_json, prop_json=properties_json)
                # Generate and save the entity pages
                self.generateTopic(topic, args.backupPath, args.overwrite)
            elif args.mode == UPDATE_TEMPLATES_MODE:
                data = {}
                if "data_input" in args:
                    with open(args.data_input) as json_file:
                        data_str = json_file.read()
                        data = json.loads(data_str)
                elif args.stdin:
                    data = json.load(sys.stdin)
                else:
                    pass
                template_data = data.get(args.template)
                exclude_keys = ["pageTitle"]
                self.update_or_create_templates(template_data, name_id="pageTitle" , template_name=args.template,exclude_keys=exclude_keys, backup_path=args.backupPath ,overwrite=args.overwrite)


            if args.mode == CREATE_FILE_MODE:
                # ToDo
                pass


        except KeyboardInterrupt:
            ### handle keyboard interrupt ###
            return 1
        except Exception as e:
            raise e
        
        return 0

    def getParser(self):
        # Setup argument parser
        super().getParser() # setup default parser arguments
        if self.parser is None:
            raise AttributeError("parser of this object should be defined at this point.")
        self.parser.add_argument("-m", "--mode", dest="mode",
                                 help="Select a mode.\n\tupdate_templates: updates the wikifiles at the provided location with the provided data\n\tcreate: creates a wikifile with the given data.",
                                 required=True)
        self.parser.add_argument('-ex', '--exclude', dest="exclude_keys",
                            help="List of keys that should be excluded")
        self.parser.add_argument('--properties', dest="properties_file", help="Json file containing properties")
        self.parser.add_argument('--topic', dest="topic_file", help="Json file containing topics")
        self.parser.add_argument('-f', dest="overwrite", action='store_true', default=False,
                                 help='If true template arguments will be overwritten with the given data if present')
        self.parser.add_argument("-t", "--template", dest="template",
                                 help="Select a template in which the data is being rendered")
        self.parser.add_argument("--templates", dest="templates_folder",
                                 help="Path to additional templates")
        self.parser.add_argument("--data", dest="data_input",
                                 help="Json file that should be used as data input")

    @staticmethod
    def getTemplateEnv(template_dir: str='/templates', additional_loader=None):
        loader = []
        if additional_loader is not None:
            loader.append(jinja2.FileSystemLoader(searchpath=additional_loader))
        script_dir = os.path.dirname(wikifile.__file__) + "/.."
        loader.append(jinja2.FileSystemLoader(script_dir + template_dir))
        loader.append(jinja2.ModuleLoader(get_python_lib() + template_dir))
        templateLoader = jinja2.ChoiceLoader(loader)
        templateEnv = jinja2.Environment(loader=templateLoader)
        return WikiRender.extend_template_env(templateEnv)

    @staticmethod
    def extend_template_env(template_env):
        """Add SMW classes and MetaModel classse to the template environment along with other use full functions"""
        template_env.globals['SMW'] = SMW
        template_env.globals['SMWPart'] = SMWPart
        template_env.globals['Form'] = Form
        template_env.globals['ListOf'] = ListOf
        template_env.globals['Query'] = Query
        template_env.globals['UML'] = UML
        template_env.globals['Property'] = Property
        template_env.globals['Topic'] = Topic
        template_env.globals['Context'] = Context
        # Further functionc
        template_env.globals['map'] = map
        return template_env

    def render_template(self, template_name: str, data: dict, exclude_keys: list = None):
        """
        Render the given data to a template
        Example:
            template_name = "Event"
            data = {"name": "SMWCon", "date": "2020", "Filename": "SMWCon 2020.wiki"}
            exclude_keys = ["Filename"]

            Results in:
            {{Event
            |name=SMWCon
            |date=2020
            }}
        Args:
            template_name: Name of the template
            data: Dictionary the keys are used translated as template arguments and the values as argument value
            exclude_keys: list of keys that should not be included in the template

        Returns:

        """
        if exclude_keys is not None:
            data = {x: data[x] for x in data if x not in exclude_keys}
        try:
            template_template = self.template_env.get_template("template.jinja")
            return template_template.render(name=template_name, properties=data)
        except Exception as e:
            print(e)
        return None

    def generateTopic(self, topic: Topic, path: str, overwrite:bool=False):
        """
        Generate all technical pages of the given topic and save them as wiki page at the given path
        Args:
            topic: topic for which the pages should be generated
            path: path to the location where the pages should be stored
            overwrite: If true the generated pages will overwrite existing pages. Otherwise only missing pages will be stored
        """
        if self.debug:
            print(f"generating topic {topic.name}")
        for part, smwPart in SMWPart.getAll(self).items():
            if self.debug:
                print(f"generating {smwPart.get_page_name(topic)}")
            page = smwPart.render_page(topic)
            WikiFile.write_to_file(path, smwPart.get_page_name(topic),page, overwrite=overwrite)

    def generateProperty(self, property:Property, path:str, overwrite:bool=False):
        if self.debug:
            print(f"generating property {property.name}")
        # generate property page
        #ToDo: Generate property page

    def update_or_create_templates(self,
                                   data: list,
                                   name_id: str,
                                   template_name: str,
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
            # Remove excluded keys
            for exclude in exclude_keys:
                del page[exclude]
            wiki_file = WikiFile(page_name, backup_path, wiki_render=self)
            if wiki_file.wikiText is None:
                # create page and store it
                page_content = self.render_template(template_name, page)
                WikiFile(path=backup_path, name=page_name, wiki_render=self, wikiText=page_content).save_to_file(
                    overwrite)
            else:
                # update existing template or create new one
                wiki_file.add_template(template_name, page)
                wiki_file.save_to_file(overwrite=overwrite)

    def render_metamodel(self):
        metamodels=MetaModelElement.get_metamodels()
        for metamodel in metamodels:
            self.generateTopic(metamodel, '/tmp/wikirender', True)


def main_module_call():
    wikirender = WikiRender()
    exitCode=wikirender.maininstance(sys.argv[1:])
    sys.exit(exitCode)

if __name__ == '__main__':
    main_module_call()
