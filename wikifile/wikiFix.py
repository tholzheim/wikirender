import io

from wikifile.wikiFile import WikiFile
from wikibot.wikipush import WikiPush
import json
import logging
import os
import csv
import sys
from wikifile.toolbox import Toolbox
from wikifile.wikiRender import WikiRender


class WikiFix(Toolbox):

    def __init__(self, fromWikiId, debug=False):
        super(WikiFix, self).__init__()
        self.wikiPush = WikiPush(fromWikiId=fromWikiId, login=True)
        self.debug = debug
        self.wikiRender = WikiRender()

    def getEventsinSeries(self, seriesName, queryField):
        """
        Get all the events given an event series and query label
        ToDo: This method is to specific for wikirender we better migrate it to openresearch -> e.g get all pageTitels of events of given series result is than passed to wikirender which handels the extraction

        Args:
            seriesName(str): Name of the series
            queryField(str): Query field used in SMW ask to get pages of subseries
        Returns:
            pageTitles(list): list of all pageTitles found in given series
        """
        query = '[[%s::%s]]' % (queryField, seriesName)
        pageTitles = self.wikiPush.query(query)
        return list(pageTitles)

    def get_Properties(self, pageDicts):
        '''
        gets the Header of the CSV
        Args:
            pageDicts: Page dictionaries
        Returns:
            Header(set): Properties found in the Events to append to CSV as a header
        '''
        if type(pageDicts) != list:
            return set(pageDicts.keys())
        else:
            header = set()
            for page in pageDicts:
                header.update(set(page.keys()))
            return header

    def exportToCsv(self, header, pageDicts, filename='dict', propertyList=None):
        '''
        Args:
            header(list): Header for the CSV File
            pageDicts(List of Dics): List of Dicts of pages
            filename(str)(optional): name of the csv file
        Returns:
            CSV file with filename
        '''
        if propertyList is not None:
            header = propertyList
        with open(filename + '.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            for page in pageDicts:
                pagelist = []
                for field in header:
                    checker = page.get(field)
                    if checker is None:
                        pagelist.append('')
                    else:
                        pagelist.append(checker)
                writer.writerow(pagelist)

    def editProperty(self, pageDict, propertyName, propertyValue):
        """
        Edit the given property in the Dict
        Args:
            pageDict(dict): Dictionary which holds the dictionary
            propertyName(str): Property to change/add
            propertyValue: Property Value to set
        Returns:
            pageDict(dict):updated page dict
        """
        pageDict[propertyName] = propertyValue
        return pageDict

    def getCSVofPages(self, pageTitles: str, wikiSonName: str):
        """
        Extracts for the given page titles the given WikiSon object and returns it as csv
        Args:
            pageTitles:
            wikiSonName:

        Returns:

        """
        pass

    def getCsv(self, pageTitles):
        '''
        converts the given pages to csv.
        Args:
            pageTitles: Page names to fetch and convert to CSV
        Returns:
            header(list): Header for CSV File
            pageDicts(List of Dics): List of Dicts of pages
        '''
        pageDicts = []
        for page in pageTitles:
            pageItem = self.wikiPush.fromWiki.getPage(page)
            wikiFile = WikiFile("sampleFile", "tmp", self.wikiRender, pageItem.text())
            pageDict = wikiFile.extract_template("Event")
            if self.debug:
                print(pageDict)
            pageDict['pageTitle'] = page
            pageDicts.append(pageDict)
            header = self.get_Properties(pageDicts)
        return header, pageDicts

    def exportWikiSonToCSVFile(self, filename: str, pageTitels: list, wikiSonName: str, pageTitleKey: str = "pageTitle",
                           properties: list = [], limitProperties: bool = False) -> str:
        """
        Exports the given given WikiSon entities corresponding to the given WikiSonName of the pages corresponding to
        the given pageTitles and returns the values as csv.

        Args:
            filename(str)(optional): name of the csv file with path
            pageTitles(list): List of all pageTitles from which the given WikiSon entity should be extracted
            wikiSonName(str): Name of the WikiSon object that should be extracted
            pageTitleKey(str): Name of the key that should be used to identify the pageTitle. This name should be distinct form other properties of the object
            properties(list): List of property names that should occur in the returned LoD. Order of the list is used as order of result. Default is null.
            limitProperties(bool): If true the resulting dicts only contain keys that are present in the given properties list any other key is removed. Otherwise all properties that are either given or defined are present in the result. Defualt is False.

        Returns:
            List of dicts containing the WikiSon entities of the given pages
        """
        csvString=self.exportWikiSonToCSV(pageTitels, wikiSonName, pageTitleKey, properties, limitProperties)
        with open(filename, 'w', newline='') as file:
            file.write(csvString)

    def exportWikiSonToCSV(self, pageTitels: list, wikiSonName: str, pageTitleKey: str = "pageTitle",
                           properties: list = [], limitProperties: bool = False) -> str:
        """
        Exports the given given WikiSon entities corresponding to the given WikiSonName of the pages corresponding to
        the given pageTitles and returns the values as csv.

        Args:
            pageTitles(list): List of all pageTitles from which the given WikiSon entity should be extracted
            wikiSonName(str): Name of the WikiSon object that should be extracted
            pageTitleKey(str): Name of the key that should be used to identify the pageTitle. This name should be distinct form other properties of the object
            properties(list): List of property names that should occur in the returned LoD. Order of the list is used as order of result. Default is null.
            limitProperties(bool): If true the resulting dicts only contain keys that are present in the given properties list any other key is removed. Otherwise all properties that are either given or defined are present in the result. Defualt is False.

        Returns:
            List of dicts containing the WikiSon entities of the given pages
        """
        lod = self.exportWikiSonToLOD(pageTitels, wikiSonName, pageTitleKey, properties, limitProperties)
        keys = lod[0].keys()  # exportWikiSonToLOD ensures that all returned recorde have the same set of keys
        csvString = ""
        csvStream=io.StringIO(csvString)
        dict_writer = csv.DictWriter(csvStream, keys)
        dict_writer.writeheader()
        dict_writer.writerows(lod)
        csvStream.seek(0)
        csvString=csvStream.read()
        return csvString

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

    def convertLODToCSV(self, pageTitles: list, wikiSon="Event"):
        """
        Converts the given LOD to csv by placing the key inside the values with the given pageTitleKey as column
        Example:
            Input:
        Args:
            pageTitles:
            wikiSon:

        Returns:
            header(list): Header for CSV File
            pageDicts(List of Dics): List of Dicts of pages
        """
        # ToDo: Ensure that the headers and values align when converting the LOD to csv
        pageDicts = []
        for pageTitle in pageTitles:
            wikiFile = self.getWikiFile(pageTitle)
            pageDict = wikiFile.extract_template(wikiSon)
            if self.debug:
                print(pageDict)
            pageDict['pageTitle'] = pageTitle
            pageDicts.append(pageDict)
            header = self.get_Properties(pageDicts)
        return header, pageDict

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
        lod = {}
        for wikifile in wikiFiles:
            if isinstance(wikifile, WikiFile):
                values = wikifile.extract_template(wikiSonName)
                if values is None:
                    values = {}
                pageTitle = wikifile.getPageTitle()
                if pageTitle is not None:
                    lod[pageTitle] = values
        return lod

    def exportCsvToWiki(self, pageContentList):
        """
            Creates a WikiSon Template of the given CSV
            Args:
                pageContentList(dict): List of Dicts of pageTitle and content of page in Wikison Format(1 row = 1 page = 1 entry)
            Returns:
                listOfFailures(str): List containing pageTitles of the pages failed to upload to wiki
        """
        listofFailures = []
        for pageContent in pageContentList:
            pageTitle = list(pageContent.keys())[0]
            try:
                page = self.wikiPush.fromWiki.getPage(pageTitle)
                page.edit(pageContent[pageTitle],
                          f"modified through csv import by {self.wikiPush.fromWiki.wikiUser.user}")
                if self.debug:
                    print('Successfully pushed the page to the wiki')
            except Exception as ex:
                listofFailures.append(pageTitle)
                if self.debug:
                    print('Error pushing to wiki')
                    print(ex)
        return listofFailures

    def prepareExportCsvContent(self, filename):
        """
        Creates a WikiSon Template of the given CSV
        Args:
            filename(str):CSV File name
        Returns:
            pageContentList(dict): List of Dicts of pagename and content of page in Wikison Format(1 row = 1 page = 1 entry)
        """
        pageContentList = []
        with open(filename, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                pageTitle = row['pageTitle']
                del row['pageTitle']
                pageText = Toolbox.dicttoWikiSon(row)
                pairDict = dict()
                pairDict[pageTitle] = pageText
                pageContentList.append(pairDict)
        return pageContentList

    def importCSVFileToWiki(self, csvFileName: str, wikiSonName: str, pageTitle: str = "pageTitle"):
        """
        Imports the given csv file to the wiki by applying the values of the rows.
        It is assumed that each row is clearly identified by one column which represents a pageTitle in the wiki
        Args:
            csvString: csv content as string
            wikiSonName(str): Name of the wikiSon object that should be updated/created
            pageTitle(str): Column name that holds the pageTitle

        Returns:
            Nothing
        """
        csvContent = self.readFile(filename=csvFileName)
        return self.importCSVContentToWiki(csvContent, wikiSonName=wikiSonName, pageTitle=pageTitle)

    def importCSVContentToWiki(self, csvString: str, wikiSonName: str, pageTitle: str = "pageTitle"):
        """
        Imports the given csv content to the wiki by applying the values of the rows.
        It is assumed that each row is clearly identified by one column which represents a pageTitle in the wiki
        Args:
            csvString: csv content as string
            wikiSonName(str): Name of the wikiSon object that should be updated/created
            pageTitle(str): Column name that holds the pageTitle

        Returns:
            Nothing
        """
        lod = self.convertCSVtoLOD(csvString, pageTitle)
        self.importLODtoWiki(lod, wikiSon=wikiSonName, titleKey=pageTitle)

    def readFile(self, filename: str) -> str:
        """
        Reads the given filename and returns it as string
        Args:
            filename: Name of the file that should be returned as string

        Returns:
            Content of the file as string
        """
        content = ""
        with open(filename, 'r') as file:
            content = file.read()
        return content

    def convertCSVtoLOD(self, csvString: str, pageTitle: str = "pageTitle"):
        """
        Converts the given csv string to a list of dicts (LOD).
        It is assumed that each row is clearly identified by one column which represents a pageTitle in the wiki
        Args:
            csvString(str): csv content as string
            pageTitle(str): Column name that holds the pageTitle

        Returns:
            List of dicts where each key represents the pageTitle and the value the WIKISon values corresponding to the page
        """
        reader = csv.DictReader(io.StringIO(csvString))
        return list(reader)

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
        pageDict = self.pagesListtoDict(data, titleKey)
        wiki_files = self.getUpdatedPages(pageDict, wikiSon)
        self.pushWikiFilesToWiki(wiki_files)

    def pagesListtoDict(self, data: list, titleKey: str = "pageTitle") -> dict:
        """
        Converts the given list of dicts to a dict in which each value is identified by the corresponding pageTitle.
        It is assumed that each dict has the pageTitle key set and that this key is unique within the list.
        Example:
            Input: [{"pageTitle":"Test Page", "label":Test}]
            Output: {"Test Page":{"label":Test}}

        Args:
            data(list): List of dicts of WikiSon values
            titleKey(str): Name of the key that holds the pageTitle. Default is "pageTitle"

        Returns:
            dict of dicts where each dict is identified by the pageTitle
        """
        res = {}
        for record in data:
            if titleKey in record:
                pageTitle = record[titleKey]
                del record[titleKey]
                res[pageTitle] = record
        return res

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
                wiki_file.getPage().edit(page_content, update_msg)

    def getUpdatedPages(self, records: dict, wikiSon: str) -> list:
        """
        Updates the wikiPages with the given values by applying the values to the WikiSon object matching the given wikiSon name.
        The update is applied by creating a WikiFile object from the page contnent in the wiki.
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
        Updates the given page with the given values

        Args:
            pageTitle(str): Title of the page that shoud be updated
            values(dict): values that should be used for the update
            wikiSon(str): Name of the WikiSon that should be updated

        Returns:
            WikiFile corresponding to the given pageTitle with the applied updates
        """
        wiki_file = self.getWikiFile(pageTitle)
        wiki_file.add_template(wikiSon, values, overwrite=True)
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


if __name__ == "__main__":
    fix = WikiFix('ormk', debug=True)
    # pageTitles= fix.getEventsinSeries('3DUI', 'Event in series')
    # header,dicts= fix.getCsv(pageTitles)
    # fix.exportToCsv(header,dicts)
    pageContentList = fix.prepareExportCsvContent('dict.csv')
    fix.exportCsvToWiki(pageContentList)
