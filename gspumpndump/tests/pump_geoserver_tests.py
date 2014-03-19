__author__ = 'Jonathan.Meyer'

import unittest
import gspumpndump.operations.pump_geoserver as pumper
import gspumpndump.config.geoserver_config as gs_conf


class PumpGeoServerTest(unittest.TestCase):
    def test_full_pump(self):
        pumper.pump_geoserver(gs_conf.GeoServerConfig())