__author__ = 'Jonathan.Meyer'

import unittest
import gspumpndump.operations.dump_geoserver as dumper
import gspumpndump.config.geoserver_config as gs_conf


class DumpGeoServerTest(unittest.TestCase):
    def test_full_dump(self):
        dumper.dump_geoserver(gs_conf.GeoServerConfig())