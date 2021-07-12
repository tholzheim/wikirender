'''
Created on 2021-03-21

@author: th
'''
import json
import re
import sys
import pkgutil
from datetime import datetime
from lodstorage.jsonable import Types, JSONAble
from wikifile.smw import SMW, Query
from .resources import metamodel


class MetaModelElement(object):
    '''
    a generic MetaModelElement
    
    to handle the technicalities of being a MetaModelElement so that derive
    MetaModelElements can focus on the MetaModel domain specific aspects
    '''

    @classmethod
    def get_samples(cls):
        samples = [{"name": "Element"}]
        return samples

    def __init__(self, propList: list = None, properties: dict = None, template=None):
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
        if propList is None:
            propList = MetaModelElement.get_prop_list_from_samples(MetaModelElement.get_samples())
        self.propList=propList
        self.fromProperties(properties)

    def fromProperties(self, properties: dict):
        '''
        initialize me from the given properties
        Args:
            properties(dict): a dictionary of properties
        '''
        if properties is None:
            properties = {}
        propMap={}
        for propName in self.propList:
            # https://stackoverflow.com/a/1176023/1497139
            # snakeName= MetaModelElement.get_snake_name(propName)
            propMap[propName]=propName
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
        # ToDo: Check if this method is still needed after migrating to camelCase property names
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


    @classmethod
    def fromJson(self, listname: str, jsonStr: str, sample: list = None):
        """
        Convert the given string to JSON and convert the values to the corresponding datatype"
        ToDo: Refactor to JSONAble (this method is redundant)
        Args:
            listname: name of the list the data is stored in
            jsonStr: data as json string that should be converted
            sample: sample data of the actual data. Used to convert the values to the correct type
        Returns:

        """

        types = Types(listname)
        types.getTypes("data", sample, 1)
        json_parsed = JSONAble()
        json_parsed.fromJson(jsonStr, types)
        return json_parsed.__dict__[listname]

    @staticmethod
    def get_parameters(attr: dict, prop_list: list):
        """
        Removes all key value pairs for which the key is not in the given prop_list.
        Args:
            attr: Dict of attributes with values that should be used for the conversion
            prop_list: List of properties that should be converted
        Returns:
            Returns list of dict containing the property names from the given prop_list with the corresponding value from attr
        """
        para_map = {}
        for para_item in [{prop: attr[prop]} for prop in prop_list]:
            para_map.update(para_item)
        return para_map

    @staticmethod
    def get_prop_list_from_samples(samples: list):
        """Returns a list of used keys by the given list of dicts"""
        prop_list = []
        for sample in samples:
            for key in sample.keys():
                if key not in prop_list:
                    prop_list.append(key)
        return prop_list

    def get_pageTitle(self, prefix:str, withNamespace=True):
        """
        Returns page name of this metamodel element. If pageTitle is not defined, it is assumed that name corresponds to the pageTitle.
        Args:
            prefix: MetaModelElement prefix e.g. properties usually have the prefix Property
            withNamespace: If true also the namespace of this property is returned. Otherwise, without namespace.
        Returns:
            Returns page name of this metamodel element.
        """
        if self.pageTitle:
            if withNamespace:
                return self.pageTitle
            else:
                return self.pageTitle.replace(f"{prefix}:", "")
        elif self.name:
            if withNamespace:
                return f"{prefix}:{self.name}"
            else:
                return self.name
        else:
            return None

    @staticmethod
    def get_metamodel_definition(file_name:str):
        '''
        Returns the metamodel specification of the given filename
        Args:
            file_name: name of the file that contains the requested metamodel definitions

        Returns:

        '''
        template = pkgutil.get_data(__name__, f"resources/metamodel/{file_name}")
        dict = json.loads(template)
        return dict

    @staticmethod
    def get_metamodels():
        metamodels=[]
        metamodels.append(Topic.get_metamodel())
        metamodels.append(Property.get_metamodel())
        metamodels.append(Context.get_metamodel())
        return metamodels

    @classmethod
    def get_metamodel(cls):
        '''

        Returns:
            Returns a topic object describing a Topic
        '''
        if cls.__name__ == MetaModelElement.__name__:
            return None
        topic_metamodel = MetaModelElement.get_metamodel_definition(f'{cls.__name__}.json')
        topic_properties_metamodel = MetaModelElement.get_metamodel_definition(f'{cls.__name__}_properties.json')
        topic = Topic.from_dict(topic_metamodel, topic_properties_metamodel)
        return topic


class Context(MetaModelElement):
    """
    A Context groups some topics like a Namespace/Package.
    This class provides helper functions and constants to render a Context to corresponding wiki pages
    """
    samples = [{
        "name": "ConfIDent",
        "since": datetime.strptime("2020-04-14","%Y-%m-%d"),
        "copyright": "ConfIDent Project",
        "master": "https://rq.bitplan.com"
    }]
    propList = MetaModelElement.get_prop_list_from_samples(samples)
    
    def __init__(self,properties: dict=None):
        super(Context,self).__init__(Context.propList,properties,)


class Topic(MetaModelElement):
    """
    Provides helper functions and constants for Topics
    """
    samples = [{"pageTitle": "Concept:Topic",
                "name": "Topic",
                "pluralName": "Topics",
                "icon": "File:Topic_icon.png",
                "iconUrl": "/images/a/ae/Index.png",
                "documentation": "A Topic is a Concept/Class/Thing/Entity",
                "wikiDocumentation": "A Topic is a Concept/Class/Thing/Entity",
                "context": "MetaModel",
                "listLimit": 7,
                "cargo": True
                }]
    # propList contains all attributes that belong to the Topic domain (needed to distinguish them from technical attributes)
    propList = MetaModelElement.get_prop_list_from_samples(samples)

    @classmethod
    def get_samples(cls):
        return Topic.samples

    def __init__(self, topic_properties: dict, properties: list=None):
        """
        Initialize topic with the given parameters
        Args:
            topic_properties: properties defining/describing the topic
            properties: properties that the topic uses
        """
        super(Topic, self).__init__(Topic.propList, properties=topic_properties)
        self.properties = properties

    def get_pageTitle(self, withNamespace=True):
        """
        Returns page name of this topic. If pageTitle is not defined, it is assumed that name corresponds to the pageTitle.
        Args:
            withNamespace: If true also the namespace of this property is returned. Otherwise, without namespace.
        Returns:
            Returns page name of this topic.
        """
        return super(Topic, self).get_pageTitle("Concept", withNamespace)


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
        res += SMW.render_parameters(oneliner, **MetaModelElement.get_parameters(self.__dict__, self.propList))
        return res + "}}"

    def get_page_link(self, withLabel=True, withDescription=False):
        """Returns a link to this page"""
        pageTitle = self.get_pageTitle()
        if withDescription:
            pageTitle += "::@@@"
        if withLabel:
            return f"[[{pageTitle}|{self.name}]]"
        else:
            return f"[[Concept:{pageTitle}]]"

    @classmethod
    def from_wiki_json(cls, topic_json, prop_json=None):
        """
        Parse given topic_json to attributes of this Topic and convert the values to proper python types.
        If prop_json is also given it will be converted to a list of Properties of this topic
        Args:
            topic_json: json string containing all information about the topic that should be created
            prop_json: json string containing all properties of this topic

        Returns:
            Topic object based on the given parameters
        """
        key = "data"
        topic_props = MetaModelElement.fromJson(key, topic_json, Topic.get_samples())
        properties = None
        if prop_json:
            properties = [Property(x) for x in MetaModelElement.fromJson("data", prop_json, Property.get_samples())]
        return Topic(topic_props[0], properties)

    @classmethod
    def from_dict(cls, topicRecord:dict, props:dict=None):
        """
        Parse given topic_json to attributes of this Topic and convert the values to proper python types.
        If prop_json is also given it will be converted to a list of Properties of this topic
        Args:
            topic_json: json string containing all information about the topic that should be created
            prop_json: json string containing all properties of this topic

        Returns:
            Topic object based on the given parameters
        """
        properties = None
        if props:
            properties = [Property(x) for x in props]
        return Topic(topicRecord, properties)

    def query_topic_overview(self, oneliner=False):
        """Returns a SMW query querying a brief description over this topic"""
        query = Query(mainlabel="-").select("Topic name::" + self.name)
        query.printout("Topic icon", "icon")
        query.printout("", "Topic")
        query.printout("Topic pluralName", "pluralName")
        query.printout("Topic documentation", "documentation")
        return query.render(oneliner=oneliner)

    def query_entities(self, limit=200, order="ascending", oneliner=False, withProperties=True, **kwargs):
        """Returns a SMW query that queries entities of this topic"""
        mainlabel = None
        if withProperties:
            mainlabel = self.name
        query = Query(mainlabel=mainlabel, limit=limit, order=order, **kwargs)
        query.select("Concept:" + self.name)
        if withProperties:
            query.printout_list_of_properties(Property.get_entity_properties(self.name, self.properties))
        return query.render(oneliner=oneliner)

    def query_examples(self, limit=10, oneliner=False, **kwargs):
        """Returns a SMW query that queries some examples of this topic entity"""
        return self.query_entities(limit=limit, order=None, searchlabel="...more examples", withProperties=False, oneliner=True, **kwargs)
        #return Query(limit=limit, searchlabel="...more examples").select("Concept:" + self.name).render(oneliner)

    def query_entity_properties(self, format="wikitable", oneliner=False):
        """Returns a SMW query querying all properties of this entity"""
        query = Query(format=format)
        query.select("Concept:Property")
        query.select("Property topic::Concept:" + self.name)
        query.printout_list_of_properties(Property.get_property_properties())
        return query.render(oneliner=oneliner)

    def query_number_entities(self, oneliner=True):
        """Returns a SMW query querying the number of entities of this topic in the wiki"""
        return Query(format="count").select("Concept:" + self.name).render(oneliner)

    def query_documentation(self, **kwargs):
        """Returns a SMW query querying the documentation of this topic"""
        query = Query(mainlabel="-", **kwargs)
        query.select("Topic name::" + self.name)
        query.printout("Topic wikiDocumentation", " ")
        return query.render()


class Property(MetaModelElement):
    """
    Provides helper functions and constants for properties
    """
    samples = [{"name": "Title",
                "label": "Offical Name",
                "type": "Special:Types/Test",
                "index": 2,
                "sortPos": 2,
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
                "topic": "Concept:Event"
                },
               # Properties that are not included in the MetaModel
               {"placeholder": "e.g. SMWCon",
                "regexp": "NaturalNumber",
                "usedFor": "Concept:Event, Concept:Event series",
                "pageTitle": "Property:Title"
                }]
    @classmethod
    def get_samples(cls):
        """Returns a list of property samples as list of dicts."""
        return Property.samples

    # propList contains all attributes that belong to the Property domain / Needed to distinguish them from technical attributes
    propList = MetaModelElement.get_prop_list_from_samples(samples)

    def __init__(self, properties: dict=None):
        """Initialize property with the given properties as attributes"""
        super(Property, self).__init__(Property.propList, properties)

    def is_used_for(self):
        """Returns the topics this property is used for/by"""
        res = []
        if self.topic:
            if isinstance(self.topic, list):
                res.extend(self.topic)
            else:
                res.append(self.topic)
        if self.usedFor:
            if isinstance(self.usedFor, list):
                res.extend(self.usedFor)
            else:
                res.append(self.usedFor)
        return res

    def get_pageTitle(self, withNamespace=True):
        """
        Returns page name of this property. If pageTitle is not defined, it is assumed that name corresponds to the pageTitle.
        Args:
            withNamespace: If true also the namespace of this property is returned. Otherwise, without namespace.
        Returns:
            Returns page name of this property.
        """
        return super(Property, self).get_pageTitle(self.__class__.__name__, withNamespace)


    @staticmethod
    def get_property_properties():
        """Returns the properties that describe properties"""
        properties_json = json.loads(pkgutil.get_data("wikifile", "/resources/metamodel/Property_properties.json"))
        properties = [Property(x) for x in properties_json]
        # Add pageTitle
        for property in properties:
            property.__dict__["pageTitle"] = f"Property:Property {property.name}"
        print([p.pageTitle for p in properties])
        return properties

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
        res += SMW.render_parameters(oneliner=oneliner, **MetaModelElement.get_parameters(self.__dict__, self.propList))
        return res + "}}"

    def get_page_link(self, name=None):
        """
        Returns a page link to this property. If a name is provided this name will be used instead
        Args:
            name: Name of the property page. If not given pageTitle of this object will be used.
        Returns:
            SMW page link to this property
        """
        if name is None:
            name = self.get_pageTitle(withNamespace=True)
        if self.label:
            return f"[[{name}|{self.label}]]"
        else:
            return f"[[{name}]]"

    def get_description_page_link(self):
        """
        Returns a page link to this property with the addition that a wiki language dependent description is shown if
        defined.
        For more details see https://www.semantic-mediawiki.org/wiki/Help:Special_property_Has_property_description
        Returns:
            SMW page link to this property
        """
        name = f"{self.get_pageTitle(withNamespace=False)}::@@@"
        return self.get_page_link(name)


    @staticmethod
    def filterLoP(lop: list, key: str, match: list, invert=False):
        """
        Filter given list of dicts by key value match
        Args:
            lop: list of dicts that should be filtered
            key: key to look for the match
            match: list of allowed values for the given key
            invert: If True all dicts that do NOT match are returned. Otherwise all dicts that match are returned
        Returns:
            List of dicts that have the given key with a matching value
        """
        if invert:
            return [p for p in lop if p.__dict__[key] not in match]
        else:
            return [p for p in lop if p.__dict__[key] in match]

    @classmethod
    def from_wiki_json(cls, prop_json):
        """
        Parse given prop_json to attributes of this Property and convert the values to proper python types
        Args:
            prop_json: json containing the property properties
        Returns:
            Property object
        """
        key = "data"
        prop_props = MetaModelElement.fromJson(key, prop_json, Property.get_samples())
        return Property(prop_props[0])



class UML:
    """
    ToDo: Migrate the functionality of this class to Topic
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
                if property.inputType == "tokens":
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
                if property.inputType == "tokens":
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

