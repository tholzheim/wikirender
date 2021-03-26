'''
Created on 2021-03-21

@author: th
'''
class MetaModelElement:
    def __init__(self, properties: dict,propMap, template):
        self.template=template
        for key in dict.keys():
            name=propMap[key]
            # decide how propMap works ...
            self.__dict[name]=properties[key]
        pass
    
    # def render() ... 
    # use self.template
    # which allows to use simplified templates like
    # """ %s do something  %s """ % (value1,value2) ..

class Property(MetaModelElement):
    """
    Provides helper functions and constants for properties
    """

    def __init__(self, properties: dict):
        if properties is None:
            properties = {}
        propMap={
            "name":"name",
            "label":"label"
        }
        # super call here ...
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


class Topic(MetaModelElement):
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