'''
Created on 2021-03-21

@author: th
'''
import json
import re
import sys


class MetaModelElement():
    '''
    a generic MetaModelElement
    
    to handle the technicalities of being a MetaModelElement so that derive
    MetaModelElements can focus on the MetaModel domain specific aspects
    '''
    def __init__(self, propList: list = None, properties: dict = None, template=None, sample=None):
        '''
        construct me from the given properties and the given propertyMap
        
        Args:
            propList(list): a list of field names
            properties(dict): a dictionary of properties
            template(str): the template to be used
            lenient(bool): if False throw an exception if invalid property names are in the properties dict
        '''
        super().__init__()
        self.template=template
        self.propList=propList
        self.fromProperties(properties)

    def fromProperties(self, properties: dict):
        '''
        initialize me from the given properties
        
        Args:
            properties(dict): a dictionary of properties
            lenient(bool): if False throw an exception if invalid property names are in the properties dict
        '''
        if properties is None:
            properties = {}
        propMap={}
        for propName in self.propList:
            # https://stackoverflow.com/a/1176023/1497139
            snakeName= MetaModelElement.get_snake_name(propName)
            propMap[propName]=snakeName
        for key in properties.keys():
            if key in propMap:
                name=propMap[key]
                value=properties[key]
                self.__dict__[name]=value
        for propName in propMap.keys():
            fieldname=propMap[propName]
            if fieldname not in self.__dict__:
                self.__dict__[fieldname]=None

    @staticmethod
    def get_snake_name(name):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    @staticmethod
    def render_parameters(parameter: list, oneliner=True):
        separator = "" if oneliner else "\n"
        res = ""
        for parameter, value in parameter:
            if isinstance(value, bool):
                label = parameter.replace("_", " ")
                res += f"|{label}{separator}"
            elif value is not None:
                label = parameter.replace("_", " ")
                res += f"|{label}={value}{separator}"
        return res

    @classmethod
    def fromJson(cls, jsonStr):
        '''
        initialize my content from the given json string

        Args:
            jsonStr(str): the json string to load
        '''
        jsonl = json.loads(jsonStr)
        if "data" in jsonl:
            lod = jsonl["data"]
        else:
            lod = jsonl
        metamodelElementList = []
        for row in lod:
            metamodelElement = cls(row)
            metamodelElementList.append(metamodelElement)
        return metamodelElementList
    # def render() ... 
    # use self.template
    # which allows to use simplified templates like
    # """ %s do something  %s """ % (value1,value2) ..


class Context(MetaModelElement):
    """
    
    """
    propList=["name"]
    
    def __init__(self,properties: dict=None):
        super(Context,self).__init__(Context.propList,properties,)


class Topic(MetaModelElement):
    """
    Provides helper functions and constants for Topics
    """
    propList=["name", "pluralName", "icon", "iconUrl", "documentation", "wikiDocumentation", "context" ]

    def __init__(self, properties: dict):
        super(Topic, self).__init__(Topic.propList, properties=properties)

    @staticmethod
    def get_samples():
        samples = [{"name": "Topic",
                    "pluralName": "Topics",
                    "icon": "File:Topic_icon.png",
                    "iconUrl": "/images/a/ae/Index.png",
                    "documentation": "A Topic is a Concept/Class/Thing/Entity",
                    "wikiDocumentation": "A Topic is a Concept/Class/Thing/Entity",
                    "context": "MetaModel",
                    "cargo": True
                    }]
        return samples

    def get_related_topics(self, properties):
        """
        Returns a list of names of topics that are related to this topic.
        Args:
            properties: List of all properties of the wiki

        Returns:
            list of names of related topics
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

    def render_entity(self, oneliner=True):
        """Render tis topic to its template represntation"""
        separator = "" if oneliner else "\n"
        res = "{{Topic" + separator
        res += MetaModelElement.render_parameters([(prop, self.__dict__[MetaModelElement.get_snake_name(prop)]) for prop in self.propList], oneliner)
        return res + "}}"

class Property(MetaModelElement):
    """
    Provides helper functions and constants for properties
    """
    
    propList=["name","label",
            "type",
            "index",
            "sortPos",
            "primaryKey",
            "mandatory",
            "namespace",
            "size",
            "uploadable",
            "defaultValue",
            "inputType",
            "allowedVaues",
            "documentation",
            "values_from",
            "showInGrid",
            "isLink",
            "nullable",
            "topic",
            "regexp",
            "used_for"]

    def __init__(self, properties: dict=None):
        super(Property,self).__init__(Property.propList,properties)

    @staticmethod
    def get_samples():
        samples = [{"name": "Title",
                    "label": "Offical Name",
                    "type": "Special:Types/Test",
                    "index": 2,
                    "sortPos":2,
                    "primaryKey": False,
                    "mandatory": True,
                    "namespace": "Test",
                    "size": 25,
                    "uploadable": False,
                    "defaultValue": "Some Title",
                    "inputType": "combobox",
                    "allowedVaues": "Tile A, Title B",
                    "documentation": " Documentation can contain\n line breaks",
                    "values_from": "property=Title",
                    "showInGrid": False,
                    "isLink": False,
                    "nullable": False,
                    "topic": "Concept:Event",
                    "regexp": "NaturalNumber",
                    "used_for": "Concept:Event, Concept:Event series"
                    }]
        return samples

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
        for property in properties:
            if "Concept:Property" in property.is_used_for():
                res.append(property)
        return sorted(res, key=lambda k: property.index if property.index is not None else sys.maxsize)   # ToDo: Add sotPos to all properties. If done exchange index with sortPos

    @staticmethod
    def get_entity_properties(entity_name: str, properties: list):
        """
        Extracts the properties of an entity form the given property list
        Args:
            entity_name: Name of the property for which the properties should be extracted
            properties: List of all properties

        Returns:
            List of all properties the are used by the given entity
        """
        res = []
        for property in properties:
            if f"Concept:{entity_name}" in property.is_used_for():
                res.append(property)
        return sorted(res, key=lambda k: property.index if property.index is not None else sys.maxsize)

    @staticmethod
    def get_primitive_properties(entity_name: str, properties: list):
        """
        Returns a list of all primitive datatype of the given entity.
        Args:
            entity_name:
            properties:

        Returns:

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
        for property in properties:
            if f"Concept:{entity_name}" in property.is_used_for() and property.type in primitive_datatypes:
                primitive_properties.append(property)
        return primitive_properties

    def render_entity(self, oneliner=True):
        """Render tis topic to its template representation"""
        separator = "" if oneliner else "\n"
        res = "{{Property" + separator
        res += MetaModelElement.render_parameters([(prop, self.__dict__[MetaModelElement.get_snake_name(prop)]) for prop in self.propList], oneliner)
        return res + "}}"


class UML:
    """
    Provides helper functions for uml generation
    """
    @staticmethod
    def get_outgoing_edges(entity_name: str, properties: list):
        """Reduce the given list of properties to those properties which have the given entity as subject"""
        outgoing_edges = []
        for property in properties:
            if f"Concept:{entity_name}" in property.is_used_for() and property.type == "Special:Types/Page" and property.values_from:
                uml_infos = {}
                uml_infos["source"] = entity_name
                if property.values_from:
                    values_from = str(property.values_from).split("=")
                    if values_from[0] == "concept":
                        uml_infos["target"] = values_from[1]
                    else:
                        continue
                if property.input_type == "tokens":
                    uml_infos["target_cardinality"] = "*"
                else:
                    uml_infos["target_cardinality"] = "1"
                uml_infos["source_cardinality"] = "*"
                uml_infos["property"] = property
                outgoing_edges.append(uml_infos)
        return outgoing_edges

    @staticmethod
    def get_incoming_edges(entity_name: str, properties: list):
        """Reduce the given list of properties to those properties which have the given entity as object"""
        incoming_edges = []
        for property in properties:
            if property.values_from == f"concept={entity_name}" and property.type == "Special:Types/Page" and property.values_from:
                uml_infos = {}
                uml_infos["target"] = entity_name
                if property.input_type == "tokens":
                    uml_infos["source_cardinality"] = "*"
                else:
                    uml_infos["source_cardinality"] = "1"
                uml_infos["target_cardinality"] = "1"
                uml_infos["property"] = property
                for source in property.is_used_for():
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
                        x.get('properties').append(edge.get('property').name)
            else:
                edge['properties'] = [edge.get('property').name]
                res.append(edge)
        return res



