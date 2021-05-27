
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


    def __init__(self,fromWikiId , debug=False):
        super(WikiFix, self).__init__()
        self.wikiPush= WikiPush(fromWikiId=fromWikiId,login=True)
        self.debug= debug
        self.wikiRender = WikiRender()


    def getEventsinSeries(self,seriesName,queryField):
        """
        Get all the events given an event series and query label
        Args:
            seriesName(str): Name of the series
            queryField(str): Query field used in SMW ask to get pages of subseries
        Returns:
            pageTitles(list): list of all pageTitles found in given series
        """
        query = '[[%s::%s]]'%(queryField,seriesName)
        pageTitles= self.wikiPush.query(query)
        return list(pageTitles)

    def get_Properties(self,pageDicts):
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
            header=set()
            for page in pageDicts:
                header.update(set(page.keys()))
            return header

    def exportToCsv(self,header,pageDicts,filename='dict',propertyList=None):
        '''
        Args:
            header(list): Header for the CSV File
            pageDicts(List of Dics): List of Dicts of pages
            filename(str)(optional): name of the csv file
        Returns:
            CSV file with filename
        '''
        if propertyList is not None:
            header= propertyList
        with open(filename+'.csv', 'w',newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            for page in pageDicts:
                pagelist=[]
                for field in header:
                    checker=page.get(field)
                    if checker is None:
                        pagelist.append('')
                    else:
                        pagelist.append(checker)
                writer.writerow(pagelist)

    def editProperty(self,pageDict, propertyName, propertyValue):
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

    def getCsv(self,pageTitles):
        '''
        converts the given pages to csv.
        Args:
            pageTitles: Page names to fetch and convert to CSV
        Returns:
            header(list): Header for CSV File
            pageDicts(List of Dics): List of Dicts of pages
        '''
        pageDicts=[]
        for page in pageTitles:
            pageItem = self.wikiPush.fromWiki.getPage(page)
            wikiFile=WikiFile("sampleFile", "tmp", self.wikiRender, pageItem.text())
            pageDict = wikiFile.extract_template("Event")
            if self.debug:
                print(pageDict)
            pageDict['pageTitle']=page
            pageDicts.append(pageDict)
            header=self.get_Properties(pageDicts)
        return header,pageDicts



    def exportCsvToWiki(self,pageContentList):
        """
            Creates a WikiSon Template of the given CSV
            Args:
                pageContentList(dict): List of Dicts of pagename and content of page in Wikison Format(1 row = 1 page = 1 entry)
            Returns:
                listOfFailures(str): List containing pageTitles of the pages failed to upload to wiki
        """
        listofFailures= []
        for pageContent in pageContentList:
            pageTitle = list(pageContent.keys())[0]
            try:
                page = self.wikiPush.fromWiki.getPage(pageTitle)
                page.edit(pageContent[pageTitle], f"modified through csv import by {self.wikiPush.fromWiki.wikiUser.user}")
                if self.debug:
                    print('Successfully pushed the page to the wiki')
            except Exception as ex:
                listofFailures.append(pageTitle)
                if self.debug:
                    print('Error pushing to wiki')
                    print(ex)
        return listofFailures

    def prepareExportCsvContent(self,filename):
        """
        Creates a WikiSon Template of the given CSV
        Args:
            filename(str):CSV File name
        Returns:
            pageContentList(dict): List of Dicts of pagename and content of page in Wikison Format(1 row = 1 page = 1 entry)
        """
        pageContentList=[]
        with open(filename, 'r') as csv_file:
            reader= csv.DictReader(csv_file)
            for row in reader:
                pageTitle=row['pageTitle']
                del row['pageTitle']
                pageText=Toolbox.dicttoWikiSon(row)
                pairDict= dict()
                pairDict[pageTitle] = pageText
                pageContentList.append(pairDict)
        return pageContentList


if __name__ == "__main__":
    fix= WikiFix('ormk',debug=True)
    # pageTitles= fix.getEventsinSeries('3DUI', 'Event in series')
    # header,dicts= fix.getCsv(pageTitles)
    # fix.exportToCsv(header,dicts)
    pageContentList = fix.prepareExportCsvContent('dict.csv')
    fix.exportCsvToWiki(pageContentList)