from __future__ import unicode_literals

__author__ = 'Jonathan.Meyer'

import logging
import logging.config
import mimetypes
import os

import requests
import lxml.etree as et

dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.config.fileConfig(os.path.join(dir, 'logging.conf'))
logger = logging.getLogger(__name__)

# Setup mimetypes for SLD and FTL so it can be auto-detected when pushing data
mimetypes.init()
mimetypes.add_type('application/vnd.ogc.sld+xml', '.sld')
mimetypes.add_type('application/html', '.ftl')


def pump_geoserver(gs_conf, input_dir='data'):
    # pump global styles
    pump_styles(gs_conf, None, input_dir)

    # pump workspaces
    pump_workspaces(gs_conf, input_dir)

    # pump global templates
    pump_templates(gs_conf, input_dir=os.path.join(input_dir, 'workspaces'))


def pump_styles(gs_conf, workspace=None, input_dir='data'):
    logger.debug('beginning styles pump from %s with config %s to workspace %s',
                 input_dir, gs_conf, workspace)

    target_url = '/styles'
    if workspace is not None:
        target_url = '/workspaces/{0}/styles'.format(workspace)

    input_path = os.path.join(input_dir, 'styles')

    non_slds = get_non_sld_style_file_names_iterable(input_path)
    for non_sld in non_slds:
        logger.debug('style: %s in %s', non_sld, input_path)
        push_input_to_geoserver(gs_conf, target_url, non_sld, input_path)

    slds = get_sld_file_names_iterable(input_path)
    for sld in slds:
        logger.debug('sld: %s in %s', sld, input_path)
        push_input_to_geoserver(gs_conf, target_url, sld, input_path, put_only=True)


def pump_templates(gs_conf, parent_url=None, input_dir='data/workspaces'):
    target_url = '/templates'
    if parent_url is not None:
        target_url = parent_url

    logger.debug('beginning template pump from %s with config %s to %s',
                 input_dir, gs_conf, target_url)

    templates = get_template_file_names_iterable(input_dir)
    for template in templates:
        logger.debug('template: %s in %s', template, input_dir)
        push_input_to_geoserver(gs_conf, target_url, template, input_dir, put_only=True)


def pump_workspaces(gs_conf, input_dir='data'):
    logger.debug('beginning workspaces pump with config %s from %s',
                 gs_conf, input_dir)

    workspace_dir = os.path.join(input_dir, 'workspaces')

    workspaces = get_subdirectories(workspace_dir)

    for workspace in workspaces:
        pump_workspace(gs_conf, workspace, os.path.join(workspace_dir, workspace))


def pump_workspace(gs_conf, workspace, input_dir):
    logger.debug('beginning workspace %s pump with config %s from %s',
                 workspace, gs_conf, input_dir)

    # pump workspace
    workspace_url = '/workspaces'
    namespace_url = '/namespaces'

    push_input_to_geoserver(gs_conf, workspace_url, workspace + '.xml', input_dir, 'workspace.xml',
                            del_params={'recurse': 'true'}, purify=True)
    push_input_to_geoserver(gs_conf, namespace_url, workspace + '.xml', input_dir, 'namespace.xml',
                            purify=True)

    # Push datastores
    datastores = get_subdirectories(os.path.join(input_dir, 'datastores'))

    for datastore in datastores:
        pump_datastore(gs_conf, datastore, workspace,
                       os.path.join(os.path.join(input_dir, 'datastores'), datastore))

    templates_url = '{0}/{1}/templates'.format(workspace_url, workspace)
    pump_templates(gs_conf, templates_url, input_dir)

    pump_styles(gs_conf, workspace, input_dir)


def pump_datastore(gs_conf, datastore, workspace, input_dir):
    logger.debug('beginning datastore %s pump to workspace %s with config %s from %s',
                 datastore, workspace, gs_conf, input_dir)

    # pump datastore
    datastore_url = '/workspaces/{0}/datastores'.format(workspace)

    push_input_to_geoserver(gs_conf, datastore_url, datastore + '.xml', input_dir, 'datastore.xml',
                            del_params={'recurse': 'true'}, purify=True)

    # pump associated featuretypes
    featuretypes_dir = os.path.join(input_dir, 'featuretypes')
    featuretypes = get_subdirectories(featuretypes_dir)

    for featuretype in featuretypes:
        pump_featuretype(gs_conf, featuretype, datastore, workspace,
                         os.path.join(featuretypes_dir, featuretype))

    templates_url = '{0}/{1}/templates' \
                    ''.format(datastore_url, datastore)
    pump_templates(gs_conf, templates_url, input_dir)


def pump_featuretype(gs_conf, featuretype, datastore, workspace, input_dir):
    logger.debug('beginning featuretype %s pump into datastore %s in workspace %s with config %s from %s',
                 featuretype, datastore, workspace, gs_conf, input_dir)

    featuretypes_url = '/workspaces/{0}/datastores/{1}/featuretypes'.format(workspace, datastore)
    layers_url = '/layers'

    push_input_to_geoserver(gs_conf, featuretypes_url, featuretype + '.xml', input_dir, 'featuretype.xml')
    push_input_to_geoserver(gs_conf, layers_url, featuretype + '.xml', input_dir, 'layer.xml',
                            purify=False, put_only=True)

    templates_url = '{0}/{1}/templates'.format(featuretypes_url, featuretype)
    pump_templates(gs_conf, templates_url, input_dir)


def push_input_to_geoserver(gs_conf, relative_url, object_name, input_path,
                            input_file=None, del_params=None, purify=False, put_only=False):
    """Master function for pushing locally stored data to GeoServer, via RESTConfig API.

    Handles all types of data for pushing data to GeoServer via the RESTConfig API.  Optional parameters allow for
    customizing the specific operations performed as necessary.

    :param gs_conf: GeoServer admin connection configuration object
    :param relative_url: url relative to REST endpoint, e.g., '/workspaces', '/styles', etc.
    :param object_name: name of target object from the REST endpoint perspective
    :param input_path: directory holding input file
    :param input_file: file holding data to push to REST endpoint
    :param del_params: dictionary of parameters to use in DELETE REST service call
    :param purify: flag indicating whether xml should be stripped of problem elements
    :param put_only: flag indicating choice of PUT over POST operation
    """
    url = gs_conf.geoserver_admin_url + relative_url

    if input_file is None:
        input_file = object_name

    data = ""
    mimetype = mimetypes.guess_type(input_file)[0]
    with open(os.path.join(input_path, input_file), 'r') as file_handle:
        data = file_handle.read()
        if purify:
            data = purify_xml(data)

    curr_url = '{0}/{1}'.format(url, object_name)

    logger.info("Pushing object '%s' file '%s' from '%s' to endpoint '%s'", object_name, input_file, input_path, url)

    # Used for pushing layers and templates as there is no supported POST operation
    if put_only:
        r = requests.get(curr_url,
                         auth=(gs_conf.username, gs_conf.password))
        if r.status_code == requests.codes.ok:
            logger.debug("Existing object found, updating...")
        elif r.status_code == requests.codes.not_found:
            logger.info("No existing object found, attempting PUT regardless")
        else:
            logger.error("Unexpected error retrieving existing data: %s, %s", r.status_code, r.text)

        r = requests.put(curr_url,
                         data=data,
                         headers={'Content-type': mimetype},
                         auth=(gs_conf.username, gs_conf.password))
        if r.status_code == requests.codes.ok or r.status_code == requests.codes.created:
            logger.debug("PUT successful")
        else:
            logger.error("Error pushing data: %s, %s", r.status_code, r.text)
    # Used for pushing all other types of data
    else:
        r = requests.get(curr_url,
                         auth=(gs_conf.username, gs_conf.password))
        if r.status_code == requests.codes.ok:
            logger.debug("Existing object found, removing...")

            r = requests.delete(curr_url,
                                params=del_params,
                                auth=(gs_conf.username, gs_conf.password))
            logger.debug("Delete response code: %s", r.status_code)

        logger.debug("Pushing new data")
        r = requests.post(url,
                          data=data,
                          headers={'Content-type': mimetype},
                          auth=(gs_conf.username, gs_conf.password))
        if r.status_code == requests.codes.created:
            logger.debug("Response header location: '%s'", r.headers['location'])
        elif r.status_code == requests.codes.forbidden or r.status_code == requests.codes.server_error:
            # Cannot post, assume existing was not deleted, attempt update
            logger.debug("Unable to POST, assuming existing un-deleted, attempting to PUT")
            r = requests.put(curr_url,
                             data=data,
                             headers={'Content-type': mimetype},
                             auth=(gs_conf.username, gs_conf.password))
            if r.status_code == requests.codes.created:
                logger.debug("PUT successful, response header location: '%s'", r.headers['location'])
            elif r.status_code == requests.codes.ok:
                logger.debug("PUT successful")
            else:
                logger.error("Error pushing data: %s, %s", r.status_code, r.text)
        elif r.status_code != requests.codes.ok:
            logger.error("Error pushing data: %s, %s", r.status_code, r.text)


def purify_xml(input_xml_string):
    """Traverse xml tree and remove any problematic elements from xml document

    Removes all atom:link elements and their parents from xml document.  This is necessary when inserting workspaces and
    datastores that have references to child featuretypes/etc. that have not be created yet.  These links are recreated
    by GeoServer once the child featuretypes/etc. are POSTed.

    :param input_xml_string: string of valid xml
    :return: purified string containing xml document
    """

    root = et.fromstring(input_xml_string)

    links = []
    for element in root.iter():
        if isinstance(element.tag, basestring):
            if 'Atom}link' in element.tag:
                links.append(element.getparent())

    for link in links:
        parent = link.getparent()
        if parent is not None:
            parent.remove(link)

    return et.tostring(root)


def get_template_file_names_iterable(input_dir):
    """

    :param input_dir:
    :return:
    """
    file_names = [
        f for f in get_files(input_dir)
        if f.endswith('.ftl')
    ]
    return file_names


def get_sld_file_names_iterable(input_dir):
    """

    :param input_dir:
    :return:
    """
    file_names = [
        f for f in get_files(input_dir)
        if f.endswith('.sld')
    ]
    return file_names


def get_non_sld_style_file_names_iterable(input_dir):
    """

    :param input_dir:
    :return:
    """
    file_names = [
        f for f in get_files(input_dir)
        if not f.endswith('.sld')
    ]
    return file_names


def get_subdirectories_excluding_string(input_dir, string):
    """

    :param input_dir:
    :param string:
    :return:
    """
    directory_names = [
        d for d in get_subdirectories(input_dir)
        if not string in d
    ]

    return directory_names


def get_files(input_dir):
    """Identifies all files within a given directory

    :param input_dir: location to search for direct child files
    :return: list of file names, empty list if none
    """
    try:
        file_names = [
            f for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]
    except OSError:
        file_names = []

    return file_names


def get_subdirectories(input_dir):
    """Identifies all subdirectories of given directory

    :param input_dir: location to search for direct child directories
    :return: list of directories, empty list if none
    """
    try:
        directory_names = [
            d for d in os.listdir(input_dir)
            if os.path.isdir(os.path.join(input_dir, d))
        ]
    except OSError:
        directory_names = []

    return directory_names
