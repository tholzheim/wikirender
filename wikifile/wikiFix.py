
from wikifile.wikiFile import WikiFile
from wikibot.wikipush import WikiPush
import json
import logging
import os
import csv
import sys
from wikifile.toolbox import Toolbox



class WikiFix(Toolbox):


    def __init__(self,fromWikiId , debug=False):
        super(WikiFix, self).__init__()
        self.page= WikiPush(fromWikiId=fromWikiId,login=True)
        self.debug= debug


    def get_Header(self,pageDicts):
        '''
        gets the Header of the CSV
        Args:
            pageDicts: Page dictionaries
        Returns:
            Header(set): Headers to append to CSV
        '''
        if type(pageDicts) != list:
            return set(pageDicts.keys())
        else:
            header=set()
            for page in pageDicts:
                header.update(set(page.keys()))
            return header

    def exportToCsv(self,header,pageDicts,filename='dict'):
        '''
        Args:
            header(list): Header for the CSV File
            pageDicts(List of Dics): List of Dicts of pages
            filename(str)(optional): name of the csv file
        Returns:
            CSV file with filename
        '''
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
            pagetext = self.page.fromWiki.getPage(page)
            pageDict = Toolbox.wikiSontoLOD(pagetext.text())
            pageDict['pageTitle']=page
            pageDicts.append(pageDict)
            header=self.get_Header(pageDicts)
        return header,pageDicts


    def importCsv(self,filename):
        with open(filename, 'r') as csv_file:
            reader= csv.DictReader(csv_file)
            for row in reader:
                pageTitle=row['pageTitle']
                del row['pageTitle']
                pageText=Toolbox.dicttoWikiSon(row)
                try:
                    page = self.page.fromWiki.getPage(pageTitle)
                    page.edit(pageText, f"modified through csv import by {self.page.fromWiki.wikiUser.user}")
                    if self.debug:
                        print('done')
                    return 1
                except Exception as ex:
                    if self.debug:
                        print('error')
                        print(ex)
                    return None


if __name__ == "__main__":
    fix= WikiFix('ormk')
    header,dicts= fix.getCsv(['3DUI 2020','3DUI 2017'])
    fix.exportToCsv(header,dicts)
    fix.importCsv('dict.csv')