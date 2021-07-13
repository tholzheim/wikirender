
from wikifile.wikiFile import WikiFile
import json
import sys
import logging

from wikifile.cmdline import CmdLineAble


class WikiExtract(CmdLineAble):
    """
    Provides methods to extract data from wiki markup files.
    """
    def __init__(self, debug=False, is_module_call=False):
        '''
        constructor
        
        Args:
            debug(bool): if True show debugging information
        '''
        self.debug=debug
        self.is_module_call=is_module_call
        super(WikiExtract, self).__init__()

    def getParser(self):
        # Setup argument parser
        super().getParser() # setup default parser arguments
        if self.parser is None:
            raise AttributeError("parser of this object should be defined at this point.")
        self.parser.add_argument("-m", "--mode", dest="mode",
                                 help="Select a mode.\n\tupdate_templates: updates the wikifiles at the provided location with the provided data\n\tcreate: creates a wikifile with the given data.",
                                 required=True)
        # Add parser arguments
        self.parser.add_argument("-t", "--template", dest="template",
                                 help="Select a template in which the data is being rendered", required=True)
        self.parser.add_argument("-id", "--file_name_id", dest="file_name_id",
                                 help="Name of the key in which the file name is stored.")
        self.parser.add_argument("--listFile", dest="file_list",
                                 help="List of pages from which the data should be extracted", required=False)

    @staticmethod
    def extract_templates(template_name: str, stdIn, page_titles, file_list, backup_path, add_file_name):
        """
        Extracts template data of the template template_name from the given files/location and returns the data as json.
        Args:
            template_name: name of the template that should be extracted
            stdIn:
            page_titles:
            file_list:
            backup_path:
            add_file_name: If defined this value will be used as key to store the filename. Should be used wisely to not interfere with regular template arguments.

        Returns:

        """
        # refactor to use command line
        res = []
        for file in page_titles:
            wikiFile = WikiFile(file, backup_path)
            template = wikiFile.extract_template(template_name)
            if template is not None:
                if add_file_name is not None:
                    template[add_file_name] = file
                res.append(template)
        return json.dumps({"data": res}, default=str, indent=3)
    
    def maininstance(self, argv=None):
        '''
        command line entry point
        
        Args:
            argv(list): command line arguments
        '''
        if argv is None:
            argv = sys.argv[1:]

        self.getParser()
        try:
            # Process arguments
            args = self.parser.parse_args(argv)
            super().initLogging(args)


            res_templates = WikiExtract.extract_templates(args.template,
                                                          stdIn=args.stdin,
                                                          file_list=args.file_list,
                                                          page_titles=args.pages,
                                                          backup_path=args.backupPath,
                                                          add_file_name=args.file_name_id)
            print(res_templates)


        except KeyboardInterrupt:
            ### handle keyboard interrupt ###
            return 1
        except Exception as e:
            print(e)

def main_module_call():
    '''
    main entry point for console script
    '''
    wikiextract = WikiExtract(is_module_call=True)
    wikiextract.maininstance()
    sys.exit

if __name__ == '__main__':
    main_module_call()
