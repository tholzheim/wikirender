import jinja2
import json
import os
import sys
import templates as jinja_templates
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import wikitextparser as wtp
from wikitextparser import WikiText, Argument, Template

WIKI_FILE_PATH = lambda path, name: f"{path}/{name}.wiki"

def render_events(templateEnv:jinja2.Environment, data):
    events = json.loads(data)
    for event in events['events']:
        try:
            event_template = templateEnv.get_template(f"event.jinja")
            res_event = event_template.render(properties=event)
            print(res_event)
        except Exception as e:
            print(e)

def render_event(templateEnv:jinja2.Environment, data):
    try:
        event_template = templateEnv.get_template(f"event.jinja")
        return event_template.render(properties=data)
    except Exception as e:
        print(e)
    return None

def get_wikiText(name, path):
    """find the wiki file by name and return it as parsed object.

    :return None if the file is not found
    """
    fname = WIKI_FILE_PATH(path, name)
    if os.path.isfile(fname):
        with open(fname, mode='r') as file:
            page = file.read()
            parsed_page = wtp.parse(page)
            return parsed_page
    return None

def get_template(wikiText:WikiText, template_name:str):
    for template in wikiText.templates:
        name = template.name
        if name.replace('\n', '') == template_name:
            return template
    return None

def update_arguments(template:Template, args, force=False):
    for key, value in args.items():
        if template.has_arg(key):
            # update argument
            if force:
                template.del_arg(key)
                template.set_arg(key, value)
            else:
                pass
        else:
            template.set_arg(key, value)

def update_or_create_template(data:list, name_id, template_name, template_env:jinja2.Environment, backup_path, force=False):
    """
    
    :param data: json data containing the information for the templates
    :param name_id: Name of the key that contains the page name
    :param template: Name of the template that should be updated or created
    :param template_env: 
    :param backup_path: path to the directory were the wiki files are stored
    :param force: If True arguments that are already defined in the template are overwritten by the given data. If False only missing data is added 
    :return: 
    """
    for page in data:
        # check if page exists
        if name_id not in page:
            continue
        page_name = page[name_id]
        parsed_page = get_wikiText(page_name, backup_path)
        if parsed_page is None:
            # create page and store it
            page_content = render_event(template_env, page)   # ToDo: Generalize to support all templates
            save_to_file(backup_path, page_name, page_content)
        else:
            # update existing template
            template = get_template(parsed_page, template_name)
            if template is None:
                # create template
                t = Template(render_event(template_env, page))
                parsed_page.insert(0,render_event(template_env, page))
                parsed_page.templates.append(t)
            else:
                update_arguments(template, page, force)
                test = str(parsed_page)
            save_to_file(backup_path, page_name, str(parsed_page), overwrite=True)


def save_to_file(path, filename, data, overwrite=False):
    """Save the given data in a file"""
    mode = 'a'
    if overwrite:
        mode = 'w'

    with open(WIKI_FILE_PATH(path, filename), mode=mode) as f:
        f.write(data)


def main(argv=None):
    templateLoader = jinja2.FileSystemLoader(searchpath=jinja_templates.__path__)
    templateEnv = jinja2.Environment(loader=templateLoader)
    try:
        # Setup argument parser
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-t", "--template", dest="template",
                            help="Select a template in which the data is being rendered", required=True)
        parser.add_argument("-id", "--page_name_id", dest="page_name_id",
                            help="Select a template in which the data is being rendered", required=True)
        parser.add_argument('-d', '--data', dest="data_input", help="Input data which should be rendered")
        parser.add_argument('--BackupPath', dest="backupPath", help="Path to store/update the wiki entries", required=True)
        parser.add_argument('-stdin', dest="stdin", action='store_true', help='Use the input from STD IN using pipes')
        parser.add_argument('-f', dest="force", action='store_true', default=False, help='If true template arguments will be overwritten with the given data if present')
        #ToDo: Add parameter to allow custom templates that can load the macros from here

        # Process arguments
        args = parser.parse_args(argv)
        data = {}
        if args.data_input:
            data = json.loads(args.data_input)
        elif args.stdin:
            data = json.load(sys.stdin)
        else:
            pass

        if args.template == "Event":
            if 'data' in data:
                events = data['data']
            else:
                pass
            update_or_create_template(events, args.page_name_id, args.template, templateEnv, args.backupPath, args.force)
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        print(e)


if __name__ == "__main__":
    sys.argv.append("-t=events")
    sys.argv.append('-d={"data":[{ "Acronym": "SMWCon 2020","Title": "SMWCon", "Year": "2020", "Description": "test value test value\\n with line break"},{ "Acronym": "SMWCon 2021","Title": "SMWCon", "Year": "2021", "Description": "test value test value\\n with line break"}]}')
    sys.argv.append("--BackupPath=events")
    sys.argv.append("-id=events")
    main(sys.argv[1:])

    scriptdir = os.path.dirname(os.path.abspath(__file__))
    template_folder = scriptdir + '../templates'
    templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    path = "/home/holzheim/wikibackup/orth_copy"
    name = "3DUI 2020"
    data=[{"Acronym":"3DUI 2020","testkey":"Test argument"},{"Acronym":"3DUI 2021","testkey":"Test argument"}]
    update_or_create_template(data, 'Acronym', 'Event', templateEnv, path)
