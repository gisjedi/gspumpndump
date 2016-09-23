import requests


class GeoServerConfig(object):
    def __init__(self,
                 geoserver_url='http://localhost:8080/geoserver',
                 username='admin',
                 password='geoserver'):
        self._geoserver_url = geoserver_url
        self._username = username
        self._password = password

        r = requests.get(self.geoserver_admin_url, auth=(self.username, self.password))
        if r.status_code != requests.codes.ok:
            raise requests.ConnectionError('Unable to connect to GeoServer REST endpoint. '
                                           'Verify your url and credentials.')

    @property
    def geoserver_url(self):
        return self._geoserver_url

    @property
    def geoserver_admin_url(self):
        return self.geoserver_url.rstrip('/') + '/rest'

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    def __repr__(self):
        return "<GeoServerConfig: geoserver_url:'{0}', username:'{1}', password:'{2}'>"\
            .format(self.geoserver_url, self.username, self.password)