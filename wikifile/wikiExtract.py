import json
import logging
import os
from wikifile.wikiFile import WikiFile


def extrat_templates(template_name: str, stdIn, page_titles, file_list, backup_path, add_file_name):
    """

    :param template_name: name of the template that should be extracted
    :param stdIn:
    :param page_titles:
    :param file_list:
    :param backup_path:
    :param add_file_name: If defined this value will be used as key to store the filename. Should be used wisely to not interfere with regular template arguments.
    :return:
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
