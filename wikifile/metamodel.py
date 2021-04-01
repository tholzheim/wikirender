'''
Created on 2021-03-21

@author: th
'''
import json
import re
import sys


class MetaModelElement(object):
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
    def render_parameters(oneliner=True, presence_is_true=False, **kwargs):
        separator = "" if oneliner else "\n"
        res = ""
        for parameter, value in kwargs.items():
            if isinstance(value, bool):
                label = parameter.replace("_", " ")
                if presence_is_true:
                    if value:
                        res += f"|{label}{separator}"
                else:
                    # ToDo: Update bool values if decided how to query wiki config
                    bool_value = "true" if value else "false"
                    res += f"|{label}={bool_value}{separator}"
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

    @staticmethod
    def get_parameters(attr: dict, prop_list: list):
        """
        Converts given attr dict to the names given in prop_list.
        Conversion is based on the name mapping applied in get_snake_name.
        Args:
            attr: Dict of attributes with values that should be used for the conversion
            prop_list: List of properties that should be converted
        Returns:
            Returns list of dict containing the property names from the given prop_list with the corresponding value from attr
        """
        para_map = {}
        for para_item in [{prop: attr[MetaModelElement.get_snake_name(prop)]} for prop in prop_list]:
            para_map.update(para_item)
        return para_map

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
        """Render tis topic to its template representation"""
        separator = "" if oneliner else "\n"
        res = "{{Topic" + separator
        res += MetaModelElement.render_parameters(oneliner, **MetaModelElement.get_parameters(self.__dict__, self.propList))
        return res + "}}"

    @staticmethod
    def get_page_link(value):
        if isinstance(value, Topic):
            return f"[[Concept:{value.name}]]"
        else:
            return f"[[Concept:{value}]]"


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
            "allowedValues",
            "documentation",
            "values_from",
            "showInGrid",
            "isLink",
            "nullable",
            "topic",
            "regexp",
            "used_for",
            "placeholder",
            "pageName"]

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
                    "used_for": "Concept:Event, Concept:Event series",
                    "pageName": "Propertry:Title"
                    }]
        return samples

    def is_used_for(self):
        """Returns the topics this property is used for/by"""
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

    def get_pageName(self, withNamespace=True):
        if self.page_name:
            return self.page_name if withNamespace else self.page_name.replace("Property:", "")
        else:
            return None

    @staticmethod
    def get_property_properties(properties: list):
        """Returns the properties that describe properties"""
        return Property.get_entity_properties(entity_name="Property", properties=properties)

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
        return sorted(res, key=lambda k: int(k.index) if k.index is not None else sys.maxsize) # ToDo: Add sortPos to all properties. If done exchange index with sortPos

    @staticmethod
    def get_primitive_properties(entity_name: str, properties: list):
        """
        Returns a list of all primitive datatype of the given entity.
        Args:
            entity_name: name of the entity for which the primitive properties should be returned
            properties: list of all properties
        Returns:
            List of primitive properties of the given entity
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
        """Render this property to its template representation"""
        separator = "" if oneliner else "\n"
        res = "{{Property" + separator
        res += MetaModelElement.render_parameters(oneliner=oneliner, **MetaModelElement.get_parameters(self.__dict__, self.propList))
        return res + "}}"

    @staticmethod
    def get_page_link(value):
        if isinstance(value, Property):
            return f"[[Property:{value.get_pageName(withNamespace=False)}|{value.label}]]"
        else:
            return f"[[Property:{value}]]"

    @staticmethod
    def get_description_page_link(value):
        if isinstance(value, Property):
            return f"[[{value.get_pageName(withNamespace=False)}::@@@|{value.label}]]"
        else:
            return f"[[{value}::@@@]]"

    @staticmethod
    def filterLoP(lop: list, key: str, match: list, invert=False):
        if invert:
            return [p for p in lop if p.__dict__[key] not in match]
        else:
            return [p for p in lop if p.__dict__[key] in match]


class UML:
    """
    Provides helper functions for uml generation
    """

    @staticmethod
    def get_outgoing_edges(entity_name: str, properties: list):
        """
        Reduce the given list of properties to those properties which have the given entity as subject
        Args:
            entity_name: Name of the entity for which the outgoing edges should be extracted
            properties: List of all properties
        Returns:
            List of dicts with each dict containing information for one edge.
        Examples: For entity_name=Project
            [{
            "target": "Goal",
            "source": "Project",
            "source_cardinality": "*",
            "target_cardinality": "1",
            "properties": <Property object>
            }]
            Means in UML:
            "Project" "*" --> "1" "Goal" : "<Property object>.name"
        """
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
        """
        Reduce the given list of properties to those properties which have the given entity as object
        Args:
            entity_name: Name of the entity for which the incoming edges should be extracted
            properties: List of all properties
        Returns:
            List of dicts with each dict containing information for one edge.
        Examples: For entity_name=Goal
            [{
            "target": "Goal",
            "source": "Project",
            "source_cardinality": "*",
            "target_cardinality": "1",
            "properties": <Property object>
            }]
            Means in UML:
            "Project" "*" --> "1" "Goal" : "<Property object>.name"
        """
        incoming_edges = []
        for property in properties:
            if property.values_from == f"concept={entity_name}" and property.type == "Special:Types/Page" and property.values_from:
                uml_infos = {}
                uml_infos["target"] = entity_name
                if property.input_type == "tokens":
                    uml_infos["target_cardinality"] = "*"
                else:
                    uml_infos["target_cardinality"] = "1"
                uml_infos["source_cardinality"] = "*"
                uml_infos["property"] = property
                for source in property.is_used_for():
                    temp_uml_infos = uml_infos.copy()
                    temp_uml_infos["source"] = source.replace("Concept:","")
                    incoming_edges.append(temp_uml_infos)
        return incoming_edges

    @staticmethod
    def get_incoming_edges_reduced(entity_name: str, properties: list):
        """
        Same as get_incoming_edges but merges the edges that come from teh same source.
        Returns a list of dict. The edges lname is stored in the kex properties.
        Args:
            entity_name: Name of the entity for which the incoming edges should be extracted
            properties: List of all properties
        Returns:
            List of dicts with each dict containing information for one edge.
        Examples:
            [{
            "target": "Goal",
            "source": "Project",
            "source_cardinality": "*",
            "target_cardinality": "*",
            "properties": ["Task goals", "Project goals"]
            }]
            Means in UML:
            "Project" "*" --> "*" "Goal" : "Task goals, Project goals"
        """
        incoming_edges  = UML.get_incoming_edges(entity_name, properties)
        res = []
        for edge in incoming_edges:
            if edge.get('source') == entity_name:
                continue
            if edge.get('source') in [x.get('source') for x in res]:
                # merge edges
                for x in res:
                    if x.get('source') == edge.get('source'):
                        x.get('properties').append(edge.get('property').name)
            else:
                edge['properties'] = [edge.get('property').name]
                res.append(edge)
        return res

