from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import re

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
        self.parser.add_argument('--BackupPath', dest="backupPath", help="Path to store/update the wiki entries",
                            required=True)
        self.parser.add_argument('-stdin', dest="stdin", action='store_true',
                            help='Use the input from STD IN using pipes')
        self.parser.add_argument('-ex', '--exclude', dest="exclude_keys",
                            help="List of keys that should be excluded")
        self.parser.add_argument('--debug', dest="debug", action='store_true', default=False, help="Enable debug mode")

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