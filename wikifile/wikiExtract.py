
from wikifile.wikiFile import WikiFile
import json
import logging
import os
import sys

from wikifile.toolbox import Toolbox


class WikiExtract(Toolbox):
    """
    Provides methods to extract data from wiki files.
    """
    def __init__(self, debug=False):
        super(WikiExtract, self).__init__()

    def main(self, argv=None):
        if argv is None:
            argv = sys.argv

        self.getParser()
        try:
            # Process arguments
            args = self.parser.parse_args(argv)
            if args.debug:
                logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
            else:
                logging.basicConfig(stream=sys.stdout, level=logging.INFO)

            file_parameters = [args.stdin, args.pages, args.file_list]
            if len(file_parameters) - (file_parameters.count(None) + file_parameters.count(False)) > 1:
                logging.error(
                    "Multiple file selection options were used. Please use only one or none to select all files in the backup folder.")
                raise Exception("Invalid parameters")

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
                                 help="List of pages form which the data should be extracted", required=False)

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
        if stdIn:
            l = []
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
            imageBackupPath = "%s/images" % backup_path
            if page_titles is None:
                page_titles = []
                for path, subdirs, files in os.walk(backup_path):
                    for name in files:
                        filename = os.path.join(path, name)[len(backup_path) + 1:]
                        if filename.endswith(".wiki"):
                            page_titles.append(filename[:-len(".wiki")])
        total = len(page_titles)
        logging.debug(f"extracting templates from {total} wikifiles.")
        res = []
        for file in page_titles:
            wikiFile = WikiFile(file, backup_path)
            template = wikiFile.extract_template(template_name)
            if template is not None:
                if add_file_name is not None:
                    template[add_file_name] = file
                res.append(template)
        return json.dumps({"data": res}, default=str, indent=3)

def main_module_call():
    wikiextract = WikiExtract(is_module_call=True)
    wikiextract.main(sys.argv[1:])
    sys.exit()

if __name__ == '__main__':
    wikiextract = WikiExtract(is_module_call=True)
    wikiextract.main(sys.argv[1:])
    sys.exit()
