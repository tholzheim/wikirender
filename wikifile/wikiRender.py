import jinja2
from distutils.sysconfig import get_python_lib
from wikifile.metamodel import Context, Topic, UML, Property


class WikiRender:
    """
    Provides functions to render json data to wiki files
    """

    def __init__(self, template_env: jinja2.Environment=None):
        if template_env is None:
            template_env=WikiRender.getTemplateEnv()
        self.template_env = template_env
        self.template_env.globals['UML'] = UML
        self.template_env.globals['Property'] = Property
        self.template_env.globals['Topic'] = Topic
        self.template_env.globals['Context'] = Context
        
    
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



