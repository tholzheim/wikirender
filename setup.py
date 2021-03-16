# ! important
# see https://stackoverflow.com/a/27868004/1497139
from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wikirender',
    version='0.0.1',

    packages=['wikifile','templates',],
    classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9'
    ],

    install_requires=[
      'wikitextparser'
    ],
    entry_points={
      'console_scripts': [
        'wikirender = wikifile.wikiRender:main',
      ],
    },
    package_data={'templates': ['*.jinja', 'templates/*.jinja']},
    author='Tim Holzheim',
    maintainer='Tim Holzheim',
    url='',
    license='Apache License',
    description='Convert Json data into wiki files or update existing files. Provides different templates to generate wiki files',
    long_description=long_description,
    long_description_content_type='text/markdown'
)