# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
 
version = 0.1

setup(
    name = "gspumpndump",
    install_requires = ['setuptools', 'requests', 'lxml'],
    packages = find_packages(),
    package_data = {
        # If any package contains *.conf files, include them:
        'gspumpndump': ['*.conf']
    },
    entry_points = {
        "console_scripts": ['gspump = gspumpndump.commands.gspump:main',
                            'gsdump = gspumpndump.commands.gsdump:main']
        },
    version = version,
    description = "Python command line application to backup and restore GeoServer configurations using the RESTConfig"
                  "API.  Supports export/import of entire GeoServer workspace/datastore/featuretype structure, "
                  "including all associated styles and Freemarker Templates.",
    author = "Jonathan Meyer",
    author_email = "jon@gisjedi.com",
    url = "http://gisjedi.com",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        ],
    )