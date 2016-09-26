import unittest
import gspumpndump.operations.pump_geoserver as pumper


class PumpGeoServerTest(unittest.TestCase):
    def test_purify_datastore_xml(self):
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
  <workspace>
    <name>sf</name>
    </workspace>
  <connectionParameters>
    <entry key="url">file:data/sf</entry>
    <entry key="namespace">http://www.openplans.org/spearfish</entry>
  </connectionParameters>
  <__default>false</__default>
  <featureTypes>
    </featureTypes>
</dataStore>"""

        self.assertEqual(output_datastore_xml,
                         pumper.purify_xml(input_datastore_xml))

    def test_purify_workspace_xml(self):

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
  <dataStores>
    </dataStores>
  <coverageStores>
    </coverageStores>
  <wmsStores>
    </wmsStores>
</workspace>"""

        self.assertEqual(output_workspace_xml,
                         pumper.purify_xml(input_workspace_xml))


    def test_purify_coveragestore_xml(self):
        input_coveragestore_xml = \
"""<coverageStore>
  <name>arcGridSample</name>
  <type>ArcGrid</type>
  <enabled>true</enabled>
  <workspace>
    <name>nurc</name>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" rel="alternate" href="http://localhost:8080/geoserver/rest/workspaces/nurc.xml" type="application/xml"/>
  </workspace>
  <__default>false</__default>
  <url>file:coverages/arc_sample/precip30min.asc</url>
  <coverages>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" rel="alternate" href="http://localhost:8080/geoserver/rest/workspaces/nurc/coveragestores/arcGridSample/coverage/Arc_Sample/coverages.xml" type="application/xml"/>
  </coverages>
</coverageStore>"""

        output_coveragestore_xml = \
"""<coverageStore>
  <name>arcGridSample</name>
  <type>ArcGrid</type>
  <enabled>true</enabled>
  <workspace>
    <name>nurc</name>
    </workspace>
  <__default>false</__default>
  <url>file:coverages/arc_sample/precip30min.asc</url>
  <coverages>
    </coverages>
</coverageStore>"""

        self.assertEqual(output_coveragestore_xml,
                         pumper.purify_xml(input_coveragestore_xml))
# TODO: test warning when encountering encrypted passwords

