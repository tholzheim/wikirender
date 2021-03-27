'''
Created on 2021-03-21

@author: th
'''
import sys
class MetaModelElement:
    '''
    a generic MetaModelElement
    
    to handle the technicalities of being a MetaModelElement so that derive
    MetaModelElements can focus on the MetaModel domain specific aspects
    '''
    def __init__(self, properties: dict,propMap:dict, template=None):
        '''
        construct me from the given properties and the given propertyMap
        
        Args:
            properties(dict): a dictionary of properties
            propMap(dict): a mapping dictionary that maps properties to fields
        '''
        self.template=template
        for key in properties.keys():
            if not key in propMap:
                raise Exception ("Invalid property '%s' for %s" % (key,type(self)))
            name=propMap[key]
            value=properties[key]
            self.__dict__[name]=value
        for propName in propMap.keys():
            fieldname=propMap[propName]
            if fieldname not in self.__dict__:
                self.__dict__[fieldname]=None
        pass
    
    # def render() ... 
    # use self.template
    # which allows to use simplified templates like
    # """ %s do something  %s """ % (value1,value2) ..
    
class Context(MetaModelElement):
    """
    """
    def __init__(self,properties: dict):
        self.propMap={
            "name":"name",
        }
        super(Context,self).__init__(properties,self.propMap)
        
        
class Topic(MetaModelElement):
    """
    Provides helper functions and constants for Topics
    """

    def __init__(self, properties: dict):
        self.propMap={
            "name":"name",
            "pluralName":"plural_name",
            "icon":"icon",
            "iconUrl":"icon_url",
            "documentation":"documentation",
            "wikiDocumentation":"wiki_documentation",
            "defaultstoremode":"defaultstoremode",
            "context":"context_name"
        }
        super(Topic,self).__init__(properties,self.propMap)
  
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

class Property(MetaModelElement):
    """
    Provides helper functions and constants for properties
    """

    def __init__(self, properties: dict):
        if properties is None:
            properties = {}
        self.propMap={
            "name":"name",
            "label":"label",
            "type":"type",
            "index":"index",
            "sortPos":"sort_pos",
            "primaryKey":"primary_key",
            "mandatory":"mandatory",
            "namespace":"namespace",
            "size":"size"
        }
        super(Property,self).__init__(properties,self.propMap)
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



