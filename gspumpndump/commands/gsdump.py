#!/usr/bin/env python
# encoding: utf-8
'''
 -- gsdump commandline tool to dump GeoServer configurations using RESTConfig API to local file system

@author:     Jonathan Meyer

@copyright:  2016 Applied Information Sciences. All rights reserved.

@contact:    jon@gisjedi.com
@deffield    updated: Updated
'''

import sys
import os

import gspumpndump.operations.dump_geoserver as dumper
import gspumpndump.config.geoserver_config as gs_conf

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2014-03-18'
__updated__ = '2016-09-22'


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = 'gsdump commandline tool to dump GeoServer configurations using RESTConfig API to local file system'
    program_license = '''%s

  Created by Jonathan Meyer on %s.
  Copyright 2014 Applied Information Sciences. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-s", "--server", dest="server", default="http://localhost:8080/geoserver",
                            help="GeoServer URL [default: %(default)s]")
        parser.add_argument("-u", "--username", dest="username", default="admin",
                            help="GeoServer admin username. [default: %(default)s]")
        parser.add_argument("-p", "--password", dest="password", default="geoserver",
                            help="GeoServer admin password. [default: %(default)s]")
        parser.add_argument("-d", "--directory", dest="directory", default="data",
                            help="relative path to directory to hold GeoServer configuration data. "
                                 "[default: %(default)s]")
        parser.add_argument('-D', '--debug', action='store_true', default=False)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        server = args.server
        username = args.username
        password = args.password
        directory = args.directory

        config = gs_conf.GeoServerConfig(server, username, password)
        print config
        dumper.dump_geoserver(config, target_dir=directory, debug=args.debug)

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())