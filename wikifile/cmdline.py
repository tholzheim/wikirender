from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import os
import sys
import logging

class CmdLineAble(object):
    """
    Bundles methods that are required by the command line tools that this file provides
    """

    def __init__(self):
        pass
        
    def getParser(self):
        '''
        setup my argument parser
        
        sets self.parser as a side effect
        
        Returns:
            ArgumentParser: the argument parser
        '''
        # Setup argument parser
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-l", "--login", dest="login", action='store_true', help="login to source wiki for access permission")
        parser.add_argument("-s", "--source", dest="source", help="source wiki id", required=True)
   
        parser.add_argument('-p', '--pages', dest="pages",  nargs='+',
                            help="Names of the pages the action should be applied to")
        parser.add_argument('--wikiTextPath', dest="backupPath", help="Path to store/update the wiki entries",
                            required=False)
        parser.add_argument('-stdin', dest="stdin", action='store_true',
                            help='Use the input from STD IN using pipes')
        parser.add_argument('--debug', dest="debug", action='store_true', default=False, help="Enable debug mode")
        self.parser=parser
        return parser

        
    def initLogging(self,args):
        '''
        initialize the logging
        '''
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
            page_titles = sys.stdin.readlines()
            pageTitlesfix = []
            for page in page_titles:
                pageTitlesfix.append(page)
            page_titles = pageTitlesfix
        elif file_list is not None:
            f = open(file_list, 'r')
            allx = f.readlines()
            page_titles = []
            for page in allx:
                page_titles.append(page)
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
