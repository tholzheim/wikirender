import json
import os
import sys
import jinja2
from distutils.sysconfig import get_python_lib

class WikiRender:
    """
    Provides functions to render json data to wiki files
    """

    regexps = {
                'Regexp:NaturalNumber': {
                    'regexp': "/^[0-9]+$!^$/",
                    'message': 'Must be a Number',
                    'or char': '!'
                }
              }

    def __init__(self, template_env: jinja2.Environment=None):
        if template_env is None:
            template_env=WikiRender.getTemplateEnv()
        self.template_env = template_env
        self.template_env.globals['UML'] = UML
        self.template_env.globals['Property'] = Property
        self.template_env.globals['Topic'] = Topic
        
    
    @staticmethod
    def getTemplateEnv():
        scriptdir = get_python_lib()
        template_folder = scriptdir + '/templates'
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
        :param template_name: Name of the template
        :param data: Dictionary the keys are used translated as template arguments and the values as argument value
        :param exclude_keys: list of keys that should not be included in the template
        :return:
        """
        if exclude_keys is not None:
            data = {x: data[x] for x in data if x not in exclude_keys}
        try:
            template_template = self.template_env.get_template("template.jinja")
            return template_template.render(name=template_name, properties=data)
        except Exception as e:
            print(e)
        return None

    def render_help_page(self, entity_name, entity_properties, properties):
        """
        Renders the help page for the given entity using the provided properties
        :param entity_name:
        :param entity_properties:
        :param properties:
        :return:
        """
        template_template = self.template_env.get_template("help_page.jinja")
        page = template_template.render(entity_name=entity_name,
                                             entity_properties=entity_properties,
                                             all_properties=properties)
        return page

    def render_list_of_page(self, entity_name, entity_properties, properties):
        template_template = self.template_env.get_template("list_of_page.jinja")
        page = template_template.render(entity_name=entity_name,
                                                entity_properties=entity_properties,
                                                all_properties=properties)
        return page

    def render_category_page(self, entity_name, entity_properties, properties):
        template_template = self.template_env.get_template("category_page.jinja")
        page = template_template.render(entity_name=entity_name,
                                             entity_properties=entity_properties,
                                             all_properties=properties)
        return page

    def render_concept_page(self, entity_name, entity_properties, properties):
        template_template = self.template_env.get_template("concept_page.jinja")
        page = template_template.render(entity_name=entity_name,
                                             entity_properties=entity_properties,
                                             all_properties=properties)
        return page

    def render_template_page(self, entity_name, entity_properties, properties):
        template_template = self.template_env.get_template("template_page.jinja")
        page = template_template.render(entity_name=entity_name,
                                        entity_properties=entity_properties,
                                        all_properties=properties)
        return page

    def render_form_page(self, entity_name, entity_properties, properties):
        template_template = self.template_env.get_template("form_page.jinja")
        page = template_template.render(entity_name=entity_name,
                                             entity_properties=entity_properties,
                                             all_properties=properties,
                                             regexps=self.regexps)
        return page


class UML:
    """
    Provides helper functions for uml generation
    """
    @staticmethod
    def get_outgoing_edges(entity_name: str, properties: list):
        """Reduce the given list of properties to those properties which have the given entity as subject"""
        outgoing_edges = []
        for property_properties in properties:
            p = Property(property_properties)
            if p.used_for == f"Concept:{entity_name}" and p.type == "Special:Types/Page" and p.values_from:
                uml_infos = {}
                uml_infos["source"] = entity_name
                if p.values_from:
                    values_from = str(p.values_from).split("=")
                    if values_from[0] == "concept":
                        uml_infos["target"] = values_from[1]
                    else:
                        continue
                if p.input_type == "tokens":
                    uml_infos["target_cardinality"] = "*"
                else:
                    uml_infos["target_cardinality"] = "1"
                uml_infos["source_cardinality"] = "*"
                uml_infos["property"] = property_properties
                outgoing_edges.append(uml_infos)
        return outgoing_edges

    @staticmethod
    def get_incoming_edges(entity_name: str, properties: list):
        """Reduce the given list of properties to those properties which have the given entity as object"""
        incoming_edges = []
        for property_properties in properties:
            p = Property(property_properties)
            if p.values_from == f"concept={entity_name}" and p.type == "Special:Types/Page" and p.values_from:
                uml_infos = {}
                uml_infos["target"] = entity_name
                if p.input_type == "tokens":
                    uml_infos["source_cardinality"] = "*"
                else:
                    uml_infos["source_cardinality"] = "1"
                uml_infos["target_cardinality"] = "1"
                uml_infos["property"] = property_properties
                for source in p.is_used_for():
                    temp_uml_infos = uml_infos.copy()
                    temp_uml_infos["source"] = source.replace("Concept:","")
                    incoming_edges.append(temp_uml_infos)
        return incoming_edges

    @staticmethod
    def get_incoming_edges_reduced(entity_name: str, properties: list):
        incoming_edges  = UML.get_incoming_edges(entity_name, properties)
        res = []
        for edge in incoming_edges:
            if edge.get('source') == entity_name:
                break
            if edge.get('source') in [x.get('source') for x in res]:
                # merge edges
                for x in res:
                    if x.get('source') == edge.get('source'):
                        x.get('properties').append(Property(edge.get('property')).name)
            else:
                edge['properties'] = [Property(edge.get('property')).name]
                res.append(edge)
        return res

class Property:
    """
    Provides helper functions and constants for properties
    """

    def __init__(self, properties: dict):
        if properties is None:
            properties = {}
        self.name = properties.get('name')
        self.label = properties.get('label')
        self.type = properties.get('type')
        self.index = properties.get('index')
        self.sort_pos = properties.get('sortPos')
        self.primary_key = properties.get('primaryKey')
        self.mandatory = properties.get('mandatory')
        self.namespace = properties.get('namespace')
        self.size = properties.get('size')
        self.uploadable = properties.get('uploadable')
        self.default_value = properties.get('defaultValue')
        self.input_type = properties.get('inputType')
        self.allowed_values = properties.get('allowedValues')
        self.documentation = properties.get('documentation')
        self.values_from = properties.get('values_from')
        self.show_in_grid = properties.get('showInGrid')
        self.is_link = properties.get('isLink')
        self.nullable = properties.get('nullable')
        self.topic = properties.get('topic')
        self.regexp = properties.get('regexp')
        self.used_for = properties.get('used_for')

    def is_used_for(self):
        """"""
        res = []
        if self.topic:
            if isinstance(self.topic, list):
                res.extend(self.topic)
            else:
                res.append(self.topic)
        if self.used_for:
            if isinstance(self.used_for, list):
                res.extend(self.used_for)
            else:
                res.append(self.used_for)
        return res

    @staticmethod
    def get_property_properties(properties: list):
        """Returns the properties that describe properties"""
        res = []
        for p in properties:
            p_obj = Property(p)
            if "Concept:Property" in p_obj.is_used_for():
                res.append(p)
        return sorted(res, key=lambda k: Property(k).index if Property(k).index is not None else sys.maxsize)   # ToDo: Add sotPos to all properties. If done exchange index with sortPos

    @staticmethod
    def get_entity_properties(entity_name: str, properties: list):
        """
        Extracts the properties of an entity form the given property list
        :param entity_name: Name of the property for which the properties should be extracted
        :param properties: List of all properties
        :return: List of all properties the are used by the given entity
        """
        res = []
        for p in properties:
            p_obj = Property(p)
            if f"Concept:{entity_name}" in p_obj.is_used_for():
                res.append(p)
        return sorted(res, key=lambda k: Property(k).index if Property(k).index is not None else sys.maxsize)

    @staticmethod
    def get_entity_property(entity_name, properties: list):
        """Returns the properties of the given entity"""
        for p in properties:
            if Property(p).name == entity_name:
                return p
        return None

    @staticmethod
    def get_primitive_properties(entity_name: str, properties: list):
        """
        Returns a list of all primitive datatype of the given entity.
        :param entity_name:
        :return:
        """
        primitive_datatypes = ["Special:Types/Boolean",
                               "Special:Types/Date",
                               "Special:Types/Code",
                               "Special:Types/Text",
                               "Special:Types/text",
                               "Special:Types/url",
                               "Special:Types/URL",
                               "Special:Types/External identifier",
                               "Special:Types/ExternalIdentifier",
                               "Special:Types/Geographic coordinate",
                               "Special:Types/Number",
                               "Special:Types/URI",
                               "Special:Types/Url",
                               "Special:Types/number",
                               "Special:Types/code"]
        primitive_properties = []
        for property_properties in properties:
            p = Property(property_properties)
            if f"Concept:{entity_name}" in p.is_used_for() and p.type in primitive_datatypes:
                primitive_properties.append(property_properties)
        return primitive_properties


class Topic:
    """
    Provides helper functions and constants for Topics
    """

    def __init__(self, properties: dict):
        self.name = properties.get('name')
        self.plural_name = properties.get('pluralName')
        self.icon = properties.get('icon')
        self.icon_url = properties.get('iconURL')
        self.documentation = properties.get('documentation')
        self.wiki_documentation = properties.get('wikiDocumentation')
        self.defaultstoremode = properties.get('defaultstoremode')
        self.context = properties.get('context')
        self.storemode = properties.get('storemode')

    def get_related_topics(self, properties):
        """
        Returns a list of names of topics that are related to this topic.
        :param properties: List of all properties of the wiki
        :return: list of names of related topics
        """
        res = set([])
        for p in UML.get_outgoing_edges(self.name, properties):
            # source (self) --> target
            res.add(p['target'])
        for p in UML.get_incoming_edges(self.name, properties):
            # source --> target (self)
            res.add(p['source'])
        if self.name in res:
            res.remove(self.name)
        return res



if __name__ == "__main__":
    # Opening JSON file
    data={}
    with open('/home/holzheim/wikibackup/test_generation/test.json') as json_file:
        data = json.load(json_file)
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    template_folder = scriptdir + '../templates'
    templateLoader = jinja2.FileSystemLoader(searchpath="../templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template_template = templateEnv.get_template("form_page.jinja")
    wiki_render = WikiRender(templateEnv)
    print(wiki_render.render_help_page("Event",data["topics"][0],data["properties"]))
    pass