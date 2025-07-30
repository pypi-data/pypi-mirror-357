# -*- coding: utf-8 -*-

import os
import logging
import traceback
from xml.dom import minidom

from thingsboard.common.utils import path_helpers
from thingsboard.endpoint.endpoint import Endpoint
from thingsboard.endpoint.runtime.node import RuntimeNode
from thingsboard.endpoint.runtime.object import RuntimeObject

class EndpointFactoryXml(object):
    """Creates an endpoint using an XML file.

    The XML file contains a model describing how the endpoint is structured using nodes, objects and attributes.
    """

    log = logging.getLogger(__name__)

    @classmethod
    def create(cls, endpoint_name: str, xml_model_file) -> Endpoint:
        endpoint = Endpoint(endpoint_name)

        try:
            path_name = path_helpers.prettify(xml_model_file)

            cls.log.info('Reading endpoint model from \'%s\'' % path_name)

            path_name = os.path.abspath(path_name)  # Convert to absolute path to make isfile() happy

            # Check if config file is present
            if os.path.isfile(path_name):
                # Parse XML config file
                xml_config_file = minidom.parse(path_name)

                if xml_config_file:
                    config_list = xml_config_file.getElementsByTagName('config')
                    """:type : list of minidom.Element"""

                    for config in config_list:
                        device_type_list = config.getElementsByTagName('deviceType')
                        """:type : list of minidom.Element"""

                        for device_type in device_type_list:
                            """:type : list of minidom.Element"""
                            print('Parsing elements for device: ' + device_type.getAttribute('typeId'))
                            cls._parse_device_type_from_xml_dom_element(endpoint, device_type)
            else:
                raise RuntimeError('Missing configuration file: %s' % path_name)
        except Exception:
            traceback.print_exc()

        # After the endpoint is fully created the presents can be announced
        #if endpoint.is_online():
        #    endpoint.announce()

        return endpoint

    @classmethod
    def _parse_device_type_from_xml_dom_element(cls, endpoint: Endpoint, device_type: minidom.Element):
        """Parses a device type from a xml dom element.
        """
        assert device_type.tagName == 'deviceType', 'Wrong DOM element name'

        node_name = device_type.getAttribute('typeId')
        runtime_node = RuntimeNode()
        runtime_node.declare_implemented_interface('NodeInterface')

        object_list = device_type.getElementsByTagName('object')
        """:type : list of minidom.Element"""
        for obj in object_list:
            object_name = obj.getAttribute('id')
            # Create endpoint object
            runtime_object = RuntimeObject()
            # Add object to the node
            runtime_node.add_object(object_name, runtime_object)

            # Get the attributes for the object node
            attribute_list = obj.getElementsByTagName('attribute')
            for attribute in attribute_list:
                cls._parse_attribute_from_xml_dom_element(runtime_object, attribute)

        assert node_name, 'No node name given!'
        assert runtime_node, 'No endpoint node object given!'
        endpoint.add_node(node_name, runtime_node)

    @classmethod
    def _parse_attribute_from_xml_dom_element(cls, runtime_object: RuntimeObject, attribute_element: minidom.Element):
        """Parses an attribute from a xml dom element.
        """
        assert attribute_element.tagName == 'attribute', 'Wrong DOM element name'

        the_name = attribute_element.getAttribute('id')
        str_type = attribute_element.getAttribute('template')
        str_constraint = attribute_element.getAttribute('constraint')

        the_type = None

        if str_type.lower() == 'bool' or str_type.lower() == 'boolean':
            the_type = bool
        elif str_type.lower() in ('short', 'long', 'integer'):
            the_type = int
        elif str_type.lower() == 'float' or str_type.lower() == 'double' or str_type.lower() == 'number':
            the_type = float
        elif str_type.lower() == 'str' or str_type.lower() == 'string':
            the_type = str

        assert the_type, 'Attribute type unknown or not set!'

        runtime_object.add_attribute(the_name, the_type, str_constraint)