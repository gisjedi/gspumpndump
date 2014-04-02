__author__ = 'Jonathan.Meyer'

import unittest
import gspumpndump.operations.pump_geoserver as pumper
import gspumpndump.config.geoserver_config as gs_conf


class PumpGeoServerTest(unittest.TestCase):
    def test_full_pump(self):
        pumper.pump_geoserver(gs_conf.GeoServerConfig())

    def test_purify_xml(self):
        input_datastore_xml = \
"""<dataStore>
  <name>sf</name>
  <enabled>true</enabled>
  <workspace>
    <name>sf</name>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" rel="alternate" href="http://localhost:8080/geoserver/rest/workspaces/sf.xml" type="application/xml"/>
  </workspace>
  <connectionParameters>
    <entry key="url">file:data/sf</entry>
    <entry key="namespace">http://www.openplans.org/spearfish</entry>
  </connectionParameters>
  <__default>false</__default>
  <featureTypes>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" rel="alternate" href="http://localhost:8080/geoserver/rest/workspaces/sf/datastores/sf/datastore/featuretypes.xml" type="application/xml"/>
  </featureTypes>
</dataStore>"""

        output_datastore_xml = \
"""<dataStore>
  <name>sf</name>
  <enabled>true</enabled>
  <connectionParameters>
    <entry key="url">file:data/sf</entry>
    <entry key="namespace">http://www.openplans.org/spearfish</entry>
  </connectionParameters>
  <__default>false</__default>
  </dataStore>"""

        self.assertEqual(output_datastore_xml,
                         pumper.purify_xml(input_datastore_xml))

        input_workspace_xml = \
"""<workspace>
  <name>sf</name>
  <dataStores>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" rel="alternate" href="http://localhost:8080/geoserver/rest/workspaces/sf/datastores.xml" type="application/xml"/>
  </dataStores>
  <coverageStores>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" rel="alternate" href="http://localhost:8080/geoserver/rest/workspaces/sf/coveragestores.xml" type="application/xml"/>
  </coverageStores>
  <wmsStores>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" rel="alternate" href="http://localhost:8080/geoserver/rest/workspaces/sf/wmsstores.xml" type="application/xml"/>
  </wmsStores>
</workspace>"""

        output_workspace_xml = \
"""<workspace>
  <name>sf</name>
  </workspace>"""

        self.assertEqual(output_workspace_xml,
                         pumper.purify_xml(input_workspace_xml))