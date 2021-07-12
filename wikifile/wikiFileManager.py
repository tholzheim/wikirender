from wikifile.wikiFile import WikiFile
from wikibot.wikipush import WikiPush
from wikifile.cmdline import CmdLineAble
from wikifile.wikiRender import WikiRender
from lodstorage.lod import LOD

class WikiFileManager(CmdLineAble):
    '''
    access to Wiki markup files for a given wiki
    '''

    def __init__(self, sourceWikiId:str, login=True,debug=False):
        '''
        constructor
        
        Args:
            fromWikiId(str): the wikiId of the wiki 
            login(bool): do we need to login to the wiki
            debug(bool): True if debugging should be switched on 
        '''
        super(WikiFileManager, self).__init__()
        self.sourceWikiId=sourceWikiId
        self.wikiPush = WikiPush(fromWikiId=sourceWikiId, login=login)
        self.debug = debug
        self.wikiRender = WikiRender()

    def importLODtoWiki(self, data: list, wikiSon: str, titleKey: str = "pageTitle"):
        """
        Uses the given data and updates the corresponding pages in the wiki.
        It is assumed that the page title is part of the dict binding the values of the dict to the corresponding page.

        Args:
            data(list): List of Dicts that should be used to update the corresponding pages in the wiki
            wikiSon(str): Name of the wikiSon object that should be updated/created
            titleKey(str): Name of the key that holds the pageTitle. Default is "pageTitle"

        Returns:

        """
        pageDict = self.pagesListToDict(data, titleKey)
        wiki_files = self.getUpdatedPages(pageDict, wikiSon)
        self.pushWikiFilesToWiki(wiki_files)


    def exportWikiSonToLOD(self, pageTitels: list, wikiSonName: str, pageTitleKey: str = "pageTitle",
                           properties: list = [], limitProperties: bool = False) -> list:
        """
        Exports the given given WikiSon entities corresponding to the given WikiSonName of the pages corresponding to
        the given pageTitles and returns the values as list of dicts.

        Args:
            pageTitles(list): List of all pageTitles from which the given WikiSon entity should be extracted
            wikiSonName(str): Name of the WikiSon object that should be extracted
            pageTitleKey(str): Name of the key that should be used to identify the pageTitle. This name should be distinct form other properties of the object
            properties(list): List of property names that should occur in the returned LoD. Order of the list is used as order of result. Default is null.
            limitProperties(bool): If true the resulting dicts only contain keys that are present in the given properties list any other key is removed. Otherwise all properties that are either given or defined are present in the result. Defualt is False.

        Returns:
            List of dicts containing the WikiSon entities of the given pages
        """
        lod = []
        for pageTitle in pageTitels:
            wikiFile = self.getWikiFile(pageTitle)
            wikiSon = wikiFile.extract_template(wikiSonName)
            if wikiSon is not None:
                wikiSon[pageTitleKey] = pageTitle
                lod.append(wikiSon)

        # Build up the set of keys
        keys = set()
        if not limitProperties:
            for record in lod:
                used_keys = {key for key in record.keys()}
                keys.update(used_keys)

        # Add key to the properties
        for key in keys:
            if key not in properties:
                properties.append(key)

        # clean up the entries by adding missing keys
        for record in lod:
            for key in properties:
                if key not in record:
                    record[key] = None
            if limitProperties:
                recordKeys=list(record.keys())
                for key in recordKeys:
                    if key not in properties:
                        del record[key]

        # order dicts according to the order of the property list
        propertyMap = {key: pos for pos, key in enumerate(properties)}
        for pos, record in enumerate(lod):
            lod[pos] = dict(sorted(record.items(), key=lambda x: propertyMap[x[0]]))
        return lod

    def convertWikiFilesToLOD(self, wikiFiles: list, wikiSonName: str):
        '''
        converts the given pagesTitles to csv by extracting the given templateName from the wikiPage corresponding to
        the given pageTitle.

        Args:
            wikiFiles(list): PageTitles to fetch and convert to CSV
            wikiSonName(str): Name of the WikiSon object that should be extracted

        Returns:
            header(list): Header for CSV File
            pageDicts(List of Dics): List of Dicts of pages
        '''
        lod = []
        for wikifile in wikiFiles:
            if isinstance(wikifile, WikiFile):
                values = wikifile.extract_template(wikiSonName)
                if values is None:
                    values = {}
                pageTitle = wikifile.getPageTitle()
                if pageTitle is not None and len(values)>0:
                    values['pageTitle']= pageTitle
                    lod.append(values)
        return lod

    def pagesListToDict(self, data: list, titleKey: str = "pageTitle", removeKey:bool=True) -> dict:
        """
        Converts the given list of dicts to a dict in which each value is identified by the corresponding pageTitle.
        It is assumed that each dict has the pageTitle key set and that this key is unique within the list.
        Example:
            Input: [{"pageTitle":"Test Page", "label":Test}]
            Output: {"Test Page":{"label":Test}}

        Args:
            data(list): List of dicts of WikiSon values
            titleKey(str): Name of the key that holds the pageTitle. Default is "pageTitle"
            removeKey(bool): if True remove the key entry of each dict

        Returns:
            dict of dicts where each dict is identified by the pageTitle
        """
        pagesDict,duplicates = LOD.getLookup(data,titleKey,withDuplicates=False)
        if len(duplicates)>0:
            raise Exception(f"there are duplicate pageTitles {duplicates}")
        if removeKey:
            for record in pagesDict.values():
                del record[titleKey] 
        return pagesDict

    def pushWikiFilesToWiki(self, wiki_files: list):
        """
        Pushes the content of the given wikiFiles to the corresponding wiki pages in the wiki
        
        Args:
            wiki_files: list of WikiFiles that should be pushed to the wiki

        Returns:
            Nothing
        """
        for wiki_file in wiki_files:
            if isinstance(wiki_file, WikiFile):
                page_content = str(wiki_file)
                update_msg = f"modified through csv import by {self.wikiPush.fromWiki.wikiUser.user}"
                page = wiki_file.getPage()
                if page is None:
                    page = self.wikiPush.fromWiki.getPage(wiki_file.getPageTitle())
                page.edit(page_content, update_msg)

    def getUpdatedPages(self, records: dict, wikiSon: str) -> list:
        """
        Updates the wikiPages with the given values by applying the values to the WikiSon object matching the given wikiSon name.
        The update is applied by creating a WikiFile object from the page content in the wiki.
        The changes are then applied in the WikiFile object.
        Note: At this point the changes are not applied to the wiki. Do do so use pushWikiFilesToWiki()

        Args:
            records(dict): dict of dicts in which the new values for a page are identified by the pageTitle
            wikiSon(str): Name of the wikiSon object that should be updated/created

        Returns:
            List of WikiFile objects with the updated content
        """
        res = []
        for pageTitle, values in records.items():
            if pageTitle is not None:
                wiki_file = self.getUpdatedPage(pageTitle, values, wikiSon)
                res.append(wiki_file)
        return res

    def getUpdatedPage(self, pageTitle: str, values: dict, wikiSon: str) -> WikiFile:
        """
        Updates the page corresponding to the given pageTitle with the given values

        Args:
            pageTitle(str): Title of the page that shoud be updated
            values(dict): values that should be used for the update
            wikiSon(str): Name of the WikiSon that should be updated

        Returns:
            WikiFile corresponding to the given pageTitle with the applied updates
        """
        wiki_file = self.getWikiFile(pageTitle)
        wiki_file.add_template(wikiSon, values, overwrite=True, prettify=True)
        return wiki_file

    def getWikiFile(self, pageTitle: str) -> WikiFile:
        """
        Queries the given page and converts it to a WikiFile.

        Args:
            pageTitle: Title of the page that should be retrieved

        Returns:
            WikiFile corresponding the the given pageTitle
        """
        pageItem = self.wikiPush.fromWiki.getPage(pageTitle)
        wiki_file = WikiFile(pageTitle, "tmp", self.wikiRender, pageItem.text())
        wiki_file.setPage(pageItem)
        return wiki_file