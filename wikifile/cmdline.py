from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import os
import sys
import logging

from lodstorage.jsonable import JSONAble, Types


class CmdLineAble(object):
    """
    Bundles methods that are required by the command line tools that this file provides
    """

    def __init__(self):
        pass
        
    def getParser(self):
        # Setup argument parser
        self.parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
        self.parser.add_argument('-p', '--pages', dest="pages",  nargs='+',
                            help="Names of the pages the action should be applied to")
        self.parser.add_argument('--wikiTextPath', dest="backupPath", help="Path to store/update the wiki entries",
                            required=True)
        self.parser.add_argument('-stdin', dest="stdin", action='store_true',
                            help='Use the input from STD IN using pipes')
        self.parser.add_argument('-ex', '--exclude', dest="exclude_keys",
                            help="List of keys that should be excluded")
        self.parser.add_argument('--debug', dest="debug", action='store_true', default=False, help="Enable debug mode")

        
    def initLogging(self,args):
        if args.debug:
            logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        else:
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)
                        

    def getPageTitlesForArgs(self,args):
        '''
        see also wikirestore in wikipush of py-3rdparty-mediawiki
        
        Args:
            args(): parsed arguments
            
        Returns:
            List of pageTitles as specified
        '''
        page_titles=args.pages
        stdIn=args.stdin
        file_list=args.file_list
        backup_path=args.backupPath
        file_parameters = [args.stdin, args.pages, args.file_list]
        if len(file_parameters) - (file_parameters.count(None) + file_parameters.count(False)) > 1:
                logging.error(
                    "Multiple file selection options were used. Please use only one or none to select all files in the backup folder.")
                raise Exception("Invalid parameters")
        if stdIn:
            backup_path = os.path.dirname(page_titles[0].strip())
            pageTitlesfix = []
            for i in page_titles:
                pageTitlesfix.append(os.path.basename(i.strip().replace('.wiki', '')))
            page_titles = pageTitlesfix
        elif file_list is not None:
            f = open(file_list, 'r')
            allx = f.readlines()
            page_titles = []
            for i in allx:
                page_titles.append(os.path.basename(i.strip()).replace('.wiki', ''))
        else:
            if backup_path is None:
                logging.warning("No backup path is defined. Please provide a path to the location were the wiki-files are stored.")
            if page_titles is None:
                page_titles = []
                for path, subdirs, files in os.walk(backup_path):
                    for name in files:
                        filename = os.path.join(path, name)[len(backup_path) + 1:]
                        if filename.endswith(".wiki"):
                            page_titles.append(filename[:-len(".wiki")])
        total = len(page_titles)
        logging.debug(f"extracting templates from {total} wikifiles.")
        return page_titles

    def fromJson(self, listname: str, jsonStr: str, sample: list = None):
        """
        Convert the given string to JSON and convert the values to the corresponding datatype"
        Args:
            listname: name of the list the data is stored in
            jsonStr: data as json string that should be converted
            sample: sample data of the actual data. Used to convert the values to the correct type
        Returns:
            
        """""
        types = Types(listname)
        types.getTypes("data", sample, 1)
        json_parsed = JSONAble()
        json_parsed.fromJson(jsonStr, types)
        return json_parsed.__dict__[listname]
