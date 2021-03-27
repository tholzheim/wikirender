'''
Created on 2021-03-07

@author: wf
'''
from wikifile.wikiRender import WikiRender
class SMWPart(object):
    '''
    a technical Semantic MediaWiki Part
    '''

    def __init__(self, part,wikiRender=None):
        '''
        Constructor
        '''
        self.part=part
        self.wikiRender=wikiRender
        self.template="%s_page.jinja" % part.lower().replace(" ","_")
        
    def render_page(self, entity_name, entity_properties, properties):
        """
        Renders the help page for the given entity using the provided properties
        :param entity_name:
        :param entity_properties:
        :param properties:
        :return: the page
        """
        template_template = self.template_env.get_template(self.template)
        page = template_template.render(entity_name=entity_name,
                                             entity_properties=entity_properties,
                                             all_properties=properties)
        return page
        
        
    @staticmethod
    def getAll(wikiRender:WikiRender):
        smwPartList=[
            SMWPart("Category"),
            SMWPart("Concept"),
            SMWPart("Form"),
            SMWPart("Template"),
            SMWPart("Help"),
            SMWPart("List of"),
            SMWPart("Properties"),
            SMWPart("PythonCode")
        ] 
        smwParts={}
        for smwPart in smwPartList:
            smwPart.wikiRender=wikiRender
            smwParts[smwPart.part]=smwPart
        return smwParts