import os

import wikifile
from wikifile.wikiFile import WikiFile
from wikifile.metamodel import Context, Topic, UML, Property
from wikifile.smw import SMWPart
import json
import sys
import jinja2
from distutils.sysconfig import get_python_lib
from wikifile.toolbox import Toolbox



class WikiRender(Toolbox):
    """
    Provides functions to render json data to wiki files
    """

    def __init__(self, argv=None, debug=False):
        if argv is None:
            argv = sys.argv
        super(WikiRender, self).__init__()
        # Modes of operation
        UPDATE_TEMPLATES_MODE = "update_templates"
        CREATE_FILE_MODE = "create"
        GENERATE_ENTITY_PAGES = "generate_entity_pages"
        modes = [UPDATE_TEMPLATES_MODE, CREATE_FILE_MODE, GENERATE_ENTITY_PAGES]
        script_dir= os.path.dirname(wikifile.__file__) + "/.." if debug else None
        self.template_env = WikiRender.getTemplateEnv(script_dir=script_dir)
        # Setup argument parser
        self.parser.add_argument("-m", "--mode", dest="mode",
                                help="Select a mode.\n\tupdate_templates: updates the wikifiles at the provided location with the provided data\n\tcreate: creates a wikifile with the given data.",
                                required=True)
        self.parser.add_argument('--properties', dest="properties_file", help="Json file containing properties")
        self.parser.add_argument('--topics', dest="topics_file", help="Json file containing topics")
        self.parser.add_argument('-f', dest="overwrite", action='store_true', default=False,
                            help='If true template arguments will be overwritten with the given data if present')
        self.parser.add_argument("-t", "--template", dest="template",
                            help="Select a template in which the data is being rendered")
        try:
            # Process arguments
            args = self.parser.parse_args(argv)
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
                if not args.properties_file or not args.topics_file:
                    raise Exception("The parameters --properties and --topics must be defined for this mode")
                # TODO:
                # use fromJson
                properties = []
                with open(args.properties_file) as json_file:
                    properties = [Property(x) for x in
                                  self.fromJson("data", json_file.read(), Property.get_samples())]
                topics = []
                with open(args.topics_file) as json_file:
                    topics = [Topic(x) for x in self.fromJson("data", json_file.read(), Topic.get_samples())]
                if args.pages is not None:
                    topics = [x for x in topics if x.name in args.pages]
                for topic in topics:
                    # Generate and save the entity pages
                    # Template
                    # TODO:
                    for part, smwPart in SMWPart.getAll(self).items():
                        page = smwPart.render_page(topic, properties)
                        WikiFile(smwPart.get_page_name(topic), args.backupPath, wiki_render=self,
                                 wikiText=page).save_to_file(args.overwrite)

            if args.mode == CREATE_FILE_MODE:
                pass


        except KeyboardInterrupt:
            ### handle keyboard interrupt ###
            return 1
        except Exception as e:
            print(e)

    @staticmethod
    def getTemplateEnv(script_dir: str=None, template_dir: str='/templates'):
        if script_dir is None:
            script_dir = get_python_lib()
        template_folder = script_dir + template_dir
        templateLoader = jinja2.FileSystemLoader(searchpath=template_folder)
        templateEnv = jinja2.Environment(loader=templateLoader)
        return templateEnv

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


if __name__ == '__main__':
    WikiRender(sys.argv[1:], debug=True)
    sys.exit()
