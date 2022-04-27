from wikifile.wikiFileManager import WikiFileManager


class WikiPage:
    """
    Provides functionalities to update the WikiSON content of a page
    """

    def __init__(self, wikiId:str, login:bool=True, debug:bool=False):
        """
        Constructor
        Args:
            wikiId: id of the wiki
            login(bool): If True login when accessing the wiki. If False updates can not be performed
            debug(bool): If True show debug messages
        """
        self.debug=debug
        self.wikiId = wikiId
        targetWikiId = self.wikiId if login else None
        self.wikiFileManager = WikiFileManager(sourceWikiId=self.wikiId, targetWikiId=targetWikiId, login=login)

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

    def getWikiSonFromPage(self, pageTitle:str, wikiSonEntity:str, includeWikiMarkup:bool=False) -> dict:
        """
        Extract the given WikiSON entity from the page with the given pageTitle
        Note: In case multiple wikiSON  entities are present on the page currently only the first one is returned
        Args:
            pageTitle: name of the page
            wikiSonEntity: name of the WikiSON entity to extract
            includeWikiMarkup: If True the WikiMarkup of the page will be added as property to the returned record

        Returns:
            dict properties of the WikiSON entity on the page
        """
        wikiFile = self.wikiFileManager.getWikiFileFromWiki(pageTitle)
        entityRecords = wikiFile.extractTemplate(wikiSonEntity)
        if len(entityRecords) >= 1:
            entityRecord = entityRecords[0]
            if includeWikiMarkup:
                entityRecord['wikiMarkup'] = wikiFile.wikiText
            return entityRecord
        else:
            return {}
