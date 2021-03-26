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
            if f"Concept:{entity_name}" in p.is_used_for() and p.type == "Special:Types/Page" and p.values_from:
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


