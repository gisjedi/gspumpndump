# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from gspumpndump import __version__

version = __version__

setup(
    name="gspumpndump",
    install_requires=['setuptools', 'requests'],
    packages=find_packages(),
    package_data={
        # If any package contains *.conf files, include them:
        'gspumpndump': ['*.conf']
    },
    entry_points={
        "console_scripts": ['gspump = gspumpndump.commands.gspump:main',
                            'gsdump = gspumpndump.commands.gsdump:main']
    },
    version=version,
    description="Python command line application to backup and restore "
                "GeoServer configurations using the RESTConfig"
                "API. Supports export/import of entire GeoServer workspace"
                " and child object structure, "
                "including all associated styles and Freemarker Templates.",
    author="Jonathan Meyer",
    author_email="jon@gisjedi.com",
    url="https://github.com/gisjedi/gspumpndump",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],
)
