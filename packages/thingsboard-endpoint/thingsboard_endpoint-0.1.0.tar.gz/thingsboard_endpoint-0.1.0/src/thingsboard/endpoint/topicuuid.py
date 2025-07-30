# -*- coding: utf-8 -*-

import traceback

from .interface import uuid


class TopicUuid(uuid.Uuid):
    """Topic based Uuid (Universally Unique Identifier)

    In the case of topic based MQTT communication the topic is used directly in order to identify objects
    """

    # When true. Example topic: 'CrazyFrogEndpoint/nodes/CrazyFrog/objects/property/attributes/version'
    # When false. Example topic: 'CrazyFrogEndpoint/CrazyFrog/property/version'
    EXTENDED_TOPIC = False

    def __init__(self, endpoint_element=None):
        super(TopicUuid, self).__init__()
        # The topic is the UUID for every object
        self._topic = None  # type: str or None

        if endpoint_element:
            from thingsboard.endpoint.attribute import Attribute
            from thingsboard.endpoint.interface.node_container import NodeContainer
            from thingsboard.endpoint.interface.object_container import ObjectContainer

            try:
                if isinstance(endpoint_element, Attribute):
                    self._topic = self._get_attribute_topic(endpoint_element)
                elif isinstance(endpoint_element, NodeContainer):
                    self._topic = self._get_node_container_topic(endpoint_element)
                elif isinstance(endpoint_element, ObjectContainer):
                    self._topic = self._get_object_container_topic(endpoint_element)
            except Exception:
                traceback.print_exc()
                raise RuntimeError('Error in TopicUuid')

    ######################################################################
    # interface.Uuid implementation
    #
    def equals(self, other):
        """Returns true if the TopicUuid is equal to the given one, false otherwise.

        :param other: The TopicUuid to check equality with
        :type other: TopicUuid
        :return:
        """
        if not self.is_valid() or not isinstance(other, TopicUuid) or not other.is_valid():
            return False
        return True if self.topic == other.topic else False

    def is_valid(self):
        return True if self.topic is not None and self.topic != '' else False

    def to_string(self):
        """
        :return: Serialized TopicUuid.
        :rtype: str
        """
        return self.topic

    ######################################################################
    # Public API
    #
    @property
    def topic(self):
        return self._topic

    # topic.setter should only be used for testing.
    @topic.setter
    def topic(self, value):
        self._topic = value

    ######################################################################
    # Private methods
    #
    def _get_attribute_topic(self, attribute):
        attr_indicator = '/attributes/' if self.EXTENDED_TOPIC else '/'
        return self._get_attribute_container_topic(attribute.get_parent()) + attr_indicator + \
               attribute.get_name()

    def _get_attribute_container_topic(self, attribute_container):
        if attribute_container is None or attribute_container.get_name() is None:
            return '<no parent>' + '/objects/' + '<no name>'
        obj_indicator = '/objects/' if self.EXTENDED_TOPIC else '/'
        return self._get_object_container_topic(attribute_container.get_parent_object_container()) + \
               obj_indicator + attribute_container.get_name()

    def _get_object_container_topic(self, object_container):
        if not object_container:
            return '<no parent>' + '/objects/' + '<no name>'
        parent_object_container = object_container.get_parent_object_container()
        if parent_object_container:
            obj_indicator = '/objects/' if self.EXTENDED_TOPIC else '/'
            return self._get_object_container_topic(parent_object_container) + obj_indicator + object_container.get_name()

        parent_node_container = object_container.get_parent_node_container()
        if parent_node_container:
            node_indicator = '/nodes/' if self.EXTENDED_TOPIC else '/'
            return self._get_node_container_topic(parent_node_container) + node_indicator + object_container.get_name()

    @staticmethod
    def _get_node_container_topic(node_container):
        # As the name of a node container is unique, we just take the name.
        return node_container.get_name()
