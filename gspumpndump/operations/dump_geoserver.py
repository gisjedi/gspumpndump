from __future__ import unicode_literals

__author__ = 'Jonathan.Meyer'

import logging
import logging.config
import requests
import os

dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.config.fileConfig(os.path.join(dir, 'logging.conf'))
logger = logging.getLogger(__name__)

PARSE_FORMAT = 'json'
DUMP_FORMAT = 'xml'

def dump_geoserver(gs_conf, target_dir='data'):
    logger.debug('beginning GeoServer dump with config %s to %s',
                 gs_conf, target_dir)

    # dump workspaces
    dump_workspaces(gs_conf, target_dir)

    #dump global styles
    dump_styles(gs_conf, None, target_dir)

    # dump global templates
    dump_templates(gs_conf, target_dir=os.path.join(target_dir, 'workspaces'))

def dump_workspaces(gs_conf, target_dir='data'):
    logger.debug('beginning workspaces dump with config %s to %s',
                 gs_conf, target_dir)

    workspace_url = '/workspaces.' + PARSE_FORMAT
    workspaces = retrieve_value_from_iterable_from_json(gs_conf, workspace_url, 'workspace')

    for workspace in workspaces:
        dump_workspace(gs_conf, workspace, target_dir)


def dump_workspace(gs_conf, workspace, target_dir='data'):

    logger.debug('beginning workspace %s dump with config %s to %s',
                 workspace, gs_conf, target_dir)

    # dump workspace
    workspace_url = '/workspaces/' + workspace
    namespace_url = '/namespaces/' + workspace

    target_path = os.path.join(target_dir, os.path.join('workspaces', workspace))

    save_response_to_file(gs_conf,
                          '{0}.{1}'.format(workspace_url, DUMP_FORMAT),
                          os.path.join(target_path, 'workspace.' + DUMP_FORMAT))
    save_response_to_file(gs_conf,
                          '{0}.{1}'.format(namespace_url, DUMP_FORMAT),
                          os.path.join(target_path, 'namespace.' + DUMP_FORMAT))

    # dump datastores
    datastore_url = workspace_url + '/datastores.' + PARSE_FORMAT

    datastores = retrieve_value_from_iterable_from_json(gs_conf, datastore_url, 'dataStore')

    for datastore in datastores:
        dump_datastore(gs_conf, datastore, workspace, target_dir)

    dump_templates(gs_conf, workspace_url, target_path)

    dump_styles(gs_conf, workspace, target_path)

def dump_datastore(gs_conf, datastore, workspace, target_dir):
    logger.debug('beginning datastore %s dump from workspace %s with config %s to %s',
                 datastore, workspace, gs_conf, target_dir)

    # dump datastore
    datastore_path = os.path.join(target_dir, 'workspaces/{0}/datastores/{1}'.format(workspace, datastore))

    datastore_url = '/workspaces/{0}/datastores/{1}'.format(workspace, datastore)

    save_response_to_file(gs_conf,
                          '{0}/datastore.{1}'.format(datastore_url, DUMP_FORMAT),
                          '{0}/datastore.{1}'.format(datastore_path, DUMP_FORMAT))

    # dump featuretypes
    featuretypes_url = '{0}/featuretypes.{1}'.format(datastore_url, PARSE_FORMAT)

    featuretypes = retrieve_value_from_iterable_from_json(gs_conf, featuretypes_url, 'featureType')

    for featuretype in featuretypes:
        dump_featuretype(gs_conf, featuretype, datastore, workspace, target_dir)

    dump_templates(gs_conf, datastore_url, datastore_path)


def dump_featuretype(gs_conf, featuretype, datastore, workspace, target_dir):
    logger.debug('beginning featuretype %s dump from datastore %s from workspace %s with config %s to %s',
                 featuretype, datastore, workspace, gs_conf, target_dir)

    featuretype_url = '/workspaces/{0}/datastores/{1}/featuretypes/{2}'.format(workspace, datastore, featuretype)
    layer_url = '/layers/{0}.{1}'.format(featuretype, DUMP_FORMAT)

    target_path = os.path.join(target_dir, 'workspaces/{0}/datastores/{1}/featuretypes/{2}'
                         .format(workspace, datastore, featuretype))
    save_response_to_file(gs_conf, featuretype_url + '.' + DUMP_FORMAT,
                          os.path.join(target_path, 'featuretype.' + DUMP_FORMAT))
    save_response_to_file(gs_conf, layer_url, os.path.join(target_path, 'layer.' + DUMP_FORMAT))

    dump_templates(gs_conf, featuretype_url, target_path)


def dump_templates(gs_conf, parent_url='', target_dir='data/workspaces'):
    logger.debug('beginning template dump from %s with config %s to %s',
                 parent_url, gs_conf, target_dir)

    templates_url = parent_url + '/templates.' + PARSE_FORMAT
    templates = retrieve_value_from_iterable_from_json(gs_conf, templates_url, 'template')

    for template in templates:
        template_url = '{0}/templates/{1}'.format(parent_url, template)
        target_file = '{0}/{1}'.format(target_dir, template)
        save_response_to_file(gs_conf, template_url, target_file)


def dump_styles(gs_conf, workspace=None, target_dir='data'):
    logger.debug('beginning styles dump from %s with config %s to %s',
                 workspace, gs_conf, target_dir)

    workspace_prefix = ''
    if workspace is not None:
        workspace_prefix = '/workspaces/' + workspace

    styles_url = workspace_prefix + '/styles.' + PARSE_FORMAT

    styles = retrieve_value_from_iterable_from_json(gs_conf, styles_url, 'style')

    for style in styles:
        logger.debug('dumping style %s%s', workspace_prefix, style)
        style_url = '{0}/styles/{1}.{2}'.format(workspace_prefix, style, DUMP_FORMAT)
        sld_url = '{0}/styles/{1}.sld'.format(workspace_prefix, style)
        target_path = os.path.join(target_dir, 'styles')
        save_response_to_file(gs_conf, style_url, os.path.join(target_path, '{0}.{1}'.format(style, DUMP_FORMAT)))
        save_response_to_file(gs_conf, sld_url, os.path.join(target_path, style + '.sld'))

def retrieve_value_from_iterable_from_json(gs_conf, relative_url, tag_singular):
    """Attempts to retrieve an iterable result parsed from GeoServer rest config endpoint at the relative url

    :param gs_conf: GeoServerConfig object with rest url, username, password configured
    :param relative_url: url relative to the GS REST config endpoint
    :param tag_singular: a string containing the singular form of the tag to retrieve name values from
    :return: either empty iterable or one with string values
    """

    return retrieve_iterable_from_json(gs_conf, relative_url, tag_singular, key_from_iterable='name')

def retrieve_iterable_from_json(gs_conf, relative_url, tag_singular, key_from_iterable=None):
    """Attempts to retrieve an iterable result parsed from GeoServer rest config endpoint at the relative url

    :param gs_conf: GeoServerConfig object with rest url, username, password configured
    :param relative_url: url relative to the GS REST config endpoint
    :param tag_singular: a string containing the singular form of the tag to retrieve name values from
    :param key_from_iterable: optional key to pull associated values from iterable
    :return: either empty iterable or one with string values
    """
    tag_plural = tag_singular + 's'

    iterable = []
    response_json = None
    try:
        response_json = retrieve_json_from_url(gs_conf, relative_url)
    except ValueError:
        logging.exception("Unable to retrieve JSON from url: %s", relative_url)

    try:
        if response_json is not None:
            iterable = response_json[tag_plural][tag_singular]
    except (KeyError, TypeError, ValueError):
        logging.debug("No %s found.", tag_plural)

    if key_from_iterable is not None:
        # Grab only name key values to place in output iterable
        try:
            iterable = [x[key_from_iterable] for x in iterable]
        except KeyError:
            logging.exception("Unable to find name keys in resulting json object")

    return iterable

def retrieve_json_from_url(gs_conf, relative_url):
    """

    :param gs_conf:
    :param relative_url:
    :return: json response
    """
    url = gs_conf.geoserver_admin_url + '/' + relative_url.lstrip('/')

    r = requests.get(url, auth=(gs_conf.username, gs_conf.password))

    response_json = r.json()
    return response_json

def save_response_to_file(gs_conf, relative_url, target_file):
    url = gs_conf.geoserver_admin_url + relative_url

    logger.info("writing file '%s' retrieved from '%s'", target_file, url)

    r = requests.get(url, auth=(gs_conf.username, gs_conf.password))

    target_dir = os.path.abspath(os.path.dirname(target_file))
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    file_handle = open(target_file, mode='w')
    file_handle.write(r.text)
    file_handle.close()


