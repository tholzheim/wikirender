import os

import wikifile
from wikifile.wikiFile import WikiFile
from wikifile.metamodel import Context, Topic, UML, Property
from wikifile.smw import SMWPart, SMW, Form, ListOf, Query
import json
import sys
import jinja2
from distutils.sysconfig import get_python_lib
from wikifile.toolbox import Toolbox


class WikiRender(Toolbox):
    """
    Provides functions to render json data to wiki files
    """

    def __init__(self, template_env=None, debug=False, is_module_call=False):
        ''' constructor
        '''
        self.debug=debug  # debug state before args.debug is available
        super(WikiRender, self).__init__()
        if template_env is None:
            template_env = WikiRender.getTemplateEnv(is_module_call)
        self.template_env = template_env
        self.extend_template_env()

    def main(self, argv=None):
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
            data = {}
            if "data_input" in args:
                data = json.loads(args.data_input)
            elif args.stdin:
                data = json.load(sys.stdin)
            else:
                pass
            if args.mode == GENERATE_ENTITY_PAGES:
                # Check if necessary parameters are set
                if not args.properties_file or not args.topic_file:
                    raise Exception("The parameters --properties and --topics must be defined for this mode")
                properties_json = ""
                with open(args.properties_file) as json_file:
                    properties_json = json_file.read()
                topic_json = ""
                with open(args.topic_file) as json_file:
                    topic_json = json_file.read()
                topic = Topic.from_wiki_json(topic_json=topic_json, prop_json=properties_json)
                # Generate and save the entity pages
                self.generateTopic(topic, args.backupPath, args.overwrite)


            if args.mode == CREATE_FILE_MODE:
                # ToDo
                pass


        except KeyboardInterrupt:
            ### handle keyboard interrupt ###
            return 1
        except Exception as e:
            print(e)

    def getParser(self):
        # Setup argument parser
        super().getParser() # setup default parser arguments
        if self.parser is None:
            raise AttributeError("parser of this object should be defined at this point.")
        self.parser.add_argument("-m", "--mode", dest="mode",
                                 help="Select a mode.\n\tupdate_templates: updates the wikifiles at the provided location with the provided data\n\tcreate: creates a wikifile with the given data.",
                                 required=True)
        self.parser.add_argument('--properties', dest="properties_file", help="Json file containing properties")
        self.parser.add_argument('--topic', dest="topic_file", help="Json file containing topics")
        self.parser.add_argument('-f', dest="overwrite", action='store_true', default=False,
                                 help='If true template arguments will be overwritten with the given data if present')
        self.parser.add_argument("-t", "--template", dest="template",
                                 help="Select a template in which the data is being rendered")

    @staticmethod
    def getTemplateEnv(is_module_call=False, template_dir: str='/templates'):
        if is_module_call:
            script_dir = get_python_lib()
        else:
            script_dir = script_dir = os.path.dirname(wikifile.__file__) + "/.."
        template_folder = script_dir + template_dir
        templateLoader = jinja2.FileSystemLoader(searchpath=template_folder)
        templateEnv = jinja2.Environment(loader=templateLoader)
        return templateEnv

    def extend_template_env(self):
        """Add SMW classes and MetaModel classse to the template environment along with other use full functions"""
        self.template_env.globals['SMW'] = SMW
        self.template_env.globals['SMWPart'] = SMWPart
        self.template_env.globals['Form'] = Form
        self.template_env.globals['ListOf'] = ListOf
        self.template_env.globals['Query'] = Query
        self.template_env.globals['UML'] = UML
        self.template_env.globals['Property'] = Property
        self.template_env.globals['Topic'] = Topic
        self.template_env.globals['Context'] = Context
        # Further functionc
        self.template_env.globals['map'] = map

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

    def generateTopic(self, topic: Topic, path: str, overwrite: bool):
        """
        Generate all technical pages of the given topic and save them as wiki page at the given path
        Args:
            topic: topic for which the pages should be generated
            path: path to the location where the pages should be stored
            overwrite: If true the generated pages will overwrite existing pages. Otherwise only missing pages will be stored
        """
        if self.debug:
            print("generating topic %s" % topic.name)
        for part, smwPart in SMWPart.getAll(self).items():
            if self.debug:
                print(f"generating {smwPart.get_page_name(topic)}")
            page = smwPart.render_page(topic)
            wiki_file = WikiFile(smwPart.get_page_name(topic), path, wiki_render=self, wikiText=page, debug=self.debug)
            wiki_file.save_to_file(overwrite)

def main_module_call():
    wikirender = WikiRender(is_module_call=True)
    wikirender.main(sys.argv[1:])
    sys.exit()

if __name__ == '__main__':
    wikirender=WikiRender()
    wikirender.main(sys.argv[1:])
    sys.exit()
