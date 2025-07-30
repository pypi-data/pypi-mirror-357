# -*- coding: utf-8 -*-

from thingsboard.endpoint.interface.object_container import ObjectContainer
from thingsboard.endpoint.exception.modification_exception import ModificationException
from thingsboard.endpoint.topicuuid import TopicUuid
from thingsboard.endpoint.object import EndpointObject


class Node(ObjectContainer):
    def __init__(self):
        super(Node, self).__init__()
        self.parent = None
        self.name = None
        self.interfaces = {}
        self.objects = {}           # type: dict[EndpointObject]

        self._update_objects()

        # TODO Implement add to annotation
        self._add_implemented_interface_to_annotation()

    def _update_objects(self):
        # Check each field of the actual node
        for field in dir(self):
            # Check if it is an attribute and ...
            attr = getattr(self, field)
            if attr:
                if isinstance(attr, EndpointObject):
                    print('Node: Got an attribute based on an EndpointObject class')

    def _add_implemented_interface_to_annotation(self):
        pass

    ######################################################################
    # Interface implementations
    #
    def get_uuid(self):
        return TopicUuid(self)

    def get_name(self):
        return self.name

    def set_name(self, name):
        # If the node already has a name (we are renaming the node)
        # then fail with a runtime exception.
        if self.name:
            raise ModificationException('The node has already a name (Renaming objects is forbidden)!')

        # Set the local name
        self.name = name

    def get_objects(self):
        return self.objects

    def get_parent_node_container(self):
        return self.parent

    def set_parent_node_container(self, node_container):
        # If the object already has a parent (we are moving the object)
        # then fail with a runtime exception.
        if self.parent:
            raise ModificationException('The parent of a Node can never be changed ' +
                                        '(Nodes can not be moved)!')

        # Set the parent
        self.parent = node_container

    def get_parent_object_container(self):
        return None

    def set_parent_object_container(self, object_container):
        raise ModificationException('A node can not have an object container as parent!')

    def attribute_has_changed_by_endpoint(self, attribute):
        if self.parent:
            self.parent.attribute_has_changed_by_endpoint(attribute)

    def attribute_has_changed_by_cloud(self, attribute):
        if self.parent:
            self.parent.attribute_has_changed_by_cloud(attribute)

    def is_node_registered_within_endpoint(self):
        return self.parent and self.parent.is_node_registered_within_endpoint()

    def find_attribute(self, location):
        """Searches for an attribute.

        :param location: List containing the 'topic levels' constructed out of the topic uuid identifying the attribute.
        :type location [str]
        :return: The endpoint object found or None
        :rtype Attribute
        """
        if location:
            if len(location) > 0:
                if location[-1] in self.get_objects():
                    # Get object from container (dictionary) by key
                    obj = self.get_objects()[location.pop()]
                    if obj:
                        return obj.find_attribute(location)
        return None

    def find_object(self, location) -> EndpointObject or None:
        """Searches for object.

        :param location: List containing the 'topic levels' constructed out of the topic uuid identifying the attribute.
        :type location [str]
        :return: The EndpointObject found or None
        """
        if location:
            if len(location) > 0:
                if location[-1] in self.get_objects():
                    # Get object from container (dictionary) by key
                    obj = self.get_objects()[location.pop()]
                    return obj
        return None
