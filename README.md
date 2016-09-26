# gspumpndump
Tool for backup and restore of GeoServer configuration. Two commands are provided respectively for this purpose: 
`gsdump` and `gspump`. Common defaults are provided for authenticating as admin with a local GeoServer instance.

_WARNING:_ No attempt is made to preserve existing data on pumps.  All workspaces defined in local data directory will
be destroyed on remote GeoServer and reconstructed according to locally stored configuration.

## Install

The tool can be simply installed from PyPI through the use of pip:

```
pip install gspumpndump
```

## Backup

The `gsdump` command will create a complete backup of all the configuration stored within a GeoServer.

_NOTE:_ It is
critical to be aware that a server with encrypted passwords will be dumped in their encrypted form. It is highly
recommended that the password storage be set to `plain text` prior to dump to ensure cross-server config portability.

Usage:
```
gsdump -s http://myhost:8080/geoserver -u admin -p password
```

The above command will save all configuration to `./data` by default.

## Restore

The `gspump` command will take the locally stored data and push it to the remote GeoServer.

_WARNING:_ No attempt is made to preserve existing data on pumps.  All workspaces defined in local data directory will
be destroyed on remote GeoServer and reconstructed according to locally stored configuration.

Usage:
```
gspump -s http://myhost:8080/geoserver -u admin -p password
```

The above command will restore data from `./data` by default.

### Data Storage:
When dumping data, tool attempts to reproduce a file structure on disk similar to that used by GeoServer RESTConfig
API endpoints.

See the following examples:

```
/rest/workspaces/examplews.xml -> /data/workspaces/examplews/workspace.xml
/rest/namespaces/examplews.xml -> /data/workspaces/examplews/namespace.xml
/rest/workspaces/examplews/datastores/exampleds.xml -> /data/workspaces/examplews/datastores/exampleds/datastore.xml
/rest/styles/example.xml -> /data/styles/example.xml
/rest/styles/example.sld -> /data/styles/example.sld
```

