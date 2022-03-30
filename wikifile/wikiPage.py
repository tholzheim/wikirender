from wikifile.wikiFileManager import WikiFileManager


class WikiPage:
    """
    Provides functionalities to update the WikiSON content of a page
    """

    def __init__(self, wikiId:str, debug:bool=False):
        """
        Constructor
        Args:
            wikiId: id of the wiki
            debug(bool): If True show debug messages
        """
        self.debug=debug
        self.wikiId = wikiId
        self.wikiFileManager = WikiFileManager(sourceWikiId=self.wikiId, targetWikiId=self.wikiId)

    def updatePageWikiSON(self, pageTitle:str, wikiSonEntity:str, props:dict, updateMsg:str=None):
        """
        updates the given wikiSonEntity in the page under the given pageTitle with the given properties
        Args:
            pageTitle(str): title of the page to update
            wikiSonEntity(str): name of the wikiSON entity to update
            props(dict): values that should be used to update the WikiSon. Value None deletes a property
            updateMsg(str): update message to show in the page revisions

        Returns:
            Nothing
        """
        wikiFile = self.wikiFileManager.getWikiFileFromWiki(pageTitle)
        wikiFile.updateTemplate(wikiSonEntity, props, prettify=True, overwrite=True)
        wikiFile.pushToWiki(msg=updateMsg)

    def getWikiSonFromPage(self, pageTitle:str, wikiSonEntity:str) -> dict:
        """
        Extract the given WikiSON entity from the page with the given pageTitle
        Note: In case multiple wikiSON  entities are present on the page currently only the first one is returned
        Args:
            pageTitle: name of the page
            wikiSonEntity: name of the WikiSON entity to extract

        Returns:
            dict properties of the WikiSON entity on the page
        """
        wikiFile = self.wikiFileManager.getWikiFileFromWiki(pageTitle)
        entities = wikiFile.extractTemplate(wikiSonEntity)
        if len(entities) >= 1:
            return entities[0]
        else:
            return {}
