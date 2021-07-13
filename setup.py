# ! important
# see https://stackoverflow.com/a/27868004/1497139
from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wikirender',
    version='0.0.14',
    packages=['wikifile','templates','templates/macros', 'wikifile/resources/metamodel'],
    classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9'
    ],

    install_requires=[
      'wikitextparser',
      'jinja2',
      'pylodstorage'
    ],
    entry_points={
      'console_scripts': [
        'wikirender = wikifile.wikiRender:main_module_call',
        'wikiextract = wikifile.wikiExtract:main_module_call',
      ],
    },
    package_data={'templates': ['*.jinja', 'templates/*.jinja','templates/macros/*.jinja'],'templates/macros': ['*.jinja', 'templates/*.jinja','templates/macros/*.jinja'], "wikifile/resources/metamodel":['*.json']},
    author='Tim Holzheim',
    maintainer='Tim Holzheim',
    url='https://github.com/tholzheim/wikirender',
    license='Apache License',
    description='Convert Json data into wiki files or update existing files. Provides different templates to generate wiki files',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
