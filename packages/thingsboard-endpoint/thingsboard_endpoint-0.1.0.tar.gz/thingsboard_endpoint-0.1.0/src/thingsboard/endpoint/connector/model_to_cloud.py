import inspect
import logging

from thingsboard.common.utils import attribute_helpers
from thingsboard.endpoint.interface import AttributeListener
from thingsboard.endpoint.endpoint import Endpoint
from thingsboard.endpoint.node import Node as EndpointNode
from thingsboard.endpoint.runtime import RuntimeNode, RuntimeObject


class Model2CloudConnector(AttributeListener):
    """Connects a class to the cloud and provides helper methods to update attributes in the cloud.

    Inheriting from this class adds the possibility to update changes to the cloud.
    In case the attributes have the 'write' constraint (shared attribute) they are able to receive changes
    (@set commands) from ThingsBoard.
    """

    log = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super(Model2CloudConnector, self).__init__(**kwargs)

        self._attribute_mapping = None
        self._endpoint_node = None

    def set_attribute_mapping(self, attribute_mapping):
        self._attribute_mapping = attribute_mapping
        if self._endpoint_node:
            self._setup_attribute_mapping()

    def set_cloud_buddy(self, endpoint_node: EndpointNode):
        """Sets the counterpart of the Model on the cloud side.
        """
        assert self._endpoint_node is None, 'Node buddy can be set only once!'
        self._endpoint_node = endpoint_node

        if self._attribute_mapping:
            # Map write attributes
            self._setup_attribute_mapping()
            # Now endpoint node is ready
            self._on_endpoint_node_created()

    def _on_endpoint_node_created(self):
        """Called after endpoint node is connected to the model.

        Reimplement this method the perform actions to be done after endpoint node is created.
        """
        pass

    def create_endpoint_node(self, endpoint: Endpoint):
        """Creates the endpoint node for this object, adds it to the endpoint and connects both objects together.
        """
        from thingsboard.endpoint.runtime import RuntimeNode
        from thingsboard.endpoint.runtime import RuntimeObject

        if self._attribute_mapping is not None:
            # Create the node which will represent this object in the cloud
            endpoint_runtime_node = RuntimeNode()
            endpoint_runtime_node.declare_implemented_interface('NodeInterface')

            # Create endpoint attributes and add them to the corresponding endpoint object
            for model_attribute_name, endpoint_attribute_mapping in self._attribute_mapping.items():
                if 'topic' in endpoint_attribute_mapping:
                    # Convert from 'human-readable topic' to 'location stack' representation
                    location_stack = self._location_stack_from_topic(endpoint_attribute_mapping['topic'])
                    # Get the endpoint object needed to add the attribute. Create object branch structure if needed
                    endpoint_runtime_object = self.create_endpoint_object(endpoint_runtime_node, location_stack.copy())

                    # Add attribute to object
                    endpoint_runtime_object.add_attribute(name=location_stack[0],
                                                          atype=endpoint_attribute_mapping['attributeType'])
                else:
                    endpoint_runtime_object = endpoint_runtime_node.find_object([endpoint_attribute_mapping['objectName'],
                                                                                'objects'])
                    if endpoint_runtime_object is None:
                        # Create object
                        endpoint_runtime_object = RuntimeObject()
                        # Add object to the node
                        endpoint_runtime_node.add_object(endpoint_attribute_mapping['objectName'], endpoint_runtime_object)

                    # Add attribute to object
                    endpoint_runtime_object.add_attribute(name=endpoint_attribute_mapping['attributeName'],
                                                         atype=endpoint_attribute_mapping['attributeType'])

            # Add node to endpoint
            endpoint.add_node(self.__class__.__name__, endpoint_runtime_node)

            # Connect endpoint node to this object
            self.set_cloud_buddy(endpoint_runtime_node)
            return endpoint_runtime_node
        else:
            self.log.warning('Attribute \'_attribute_mapping\' needs to be initialized to create endpoint node!')
        return None

    def create_endpoint_object(self, endpoint_element : RuntimeNode | RuntimeObject, 
                               location_stack : list[str]) -> RuntimeObject:
        """Creates and returns the object structure described in location stack.
        
        If the object structure is already present in the node, the last branch object is returned.

        :param endpoint_element The node/object in where to search for the endpoint object
        :param location_stack The location stack
        """
        from thingsboard.endpoint.topicuuid import TopicUuid

        if TopicUuid.EXTENDED_TOPIC:
            object_stack = location_stack[-2:]  # Get next branch information (last two elements)
            location_stack = location_stack[:-2]  # and remove it from location stack
        else:
            object_stack = location_stack[-1:]  # Get next branch information (last element)
            location_stack = location_stack[:-1]  # and remove it from location stack

        # Check if object is already present in the tree
        endpoint_runtime_object = endpoint_element.find_object(object_stack.copy())
        if not endpoint_runtime_object:
            from thingsboard.endpoint.runtime import RuntimeObject

            # Create object
            endpoint_runtime_object = RuntimeObject()
            # Add object to the node (or object)
            endpoint_element.add_object(object_stack[0], endpoint_runtime_object)

        # First element in the location stack is the name of the attribute
        # In case there is only one element left in the location_stack the 'object structure'
        # is completely created
        if len(location_stack) == 1:
            return endpoint_runtime_object
        else:
            # Continue recursively create/get objects
            return self.create_endpoint_object(endpoint_runtime_object, location_stack)

    def _setup_attribute_mapping(self):
        assert self._attribute_mapping
        assert self._endpoint_node

        for model_attribute_name, endpoint_attribute_mapping in self._attribute_mapping.items():
            # Add listener to attributes that can be changed from the cloud (constraint: 'write')
            if 'write' in endpoint_attribute_mapping['constraints']:
                if 'topic' in endpoint_attribute_mapping:
                    # take new style

                    # Convert from 'human-readable topic' to 'location stack' representation
                    location_stack = self._location_stack_from_topic(endpoint_attribute_mapping['topic'])
                else:
                    self.log.warning('Mapping entries \'objectName\' and \'attributeName\' will be replaced by '
                                     '\'topic\' in future releases! Consider updating your code!')
                    location_stack = [endpoint_attribute_mapping['attributeName'], 'attributes',
                                      endpoint_attribute_mapping['objectName'], 'objects']
                endpoint_attribute_object = self._endpoint_node.find_attribute(location_stack)

                if endpoint_attribute_object:
                    endpoint_attribute_object.add_listener(self)
                else:
                    if 'topic' in endpoint_attribute_mapping:
                        self.log.warning('Could not map to Endpoint attribute. Endpoint.iO attribute '
                                         f'\'{endpoint_attribute_mapping['topic']}\' not found!')
                    else:
                        self.log.warning('Could not map to Endpoint attribute. Endpoint attribute '
                                         f'\'{endpoint_attribute_mapping['objectName']}/'
                                         f'{endpoint_attribute_mapping['attributeName']}\' not found!')

    def _location_stack_from_topic(self, topic, take_raw_topic=False) -> list[str]:
        """Converts attribute topic from 'human-readable topic' to 'location stack' representation.

        :return A list containing the location stack

        Example:
            topic: 'afe.core.properties.user-pwm-enable' gets converted to
            location_stack: ['user-pwm-enable', 'attributes', 'properties', 'objects', 'core', 'objects']
        """
        from thingsboard.endpoint.topicuuid import TopicUuid
        assert isinstance(topic, str)

        topic_levels = topic.split('.')
        # Remove first entry if it is the name of the endpoint node
        if not take_raw_topic and self._endpoint_node and topic_levels[0] == self._endpoint_node.get_name():
            topic_levels = topic_levels[1:]

        if TopicUuid.EXTENDED_TOPIC:
            # Add entries 'objects' and 'attributes' as needed
            expanded_topic_levels = []
            for index, topic_level in enumerate(topic_levels):
                if index < len(topic_levels) - 1:
                    expanded_topic_levels.append('objects')
                else:
                    expanded_topic_levels.append('attributes')
                expanded_topic_levels.append(topic_level)
        else:
            expanded_topic_levels = topic_levels

        # Reverse topic_level entries
        location_stack = expanded_topic_levels[::-1]
        return location_stack

    def attribute_has_changed(self, endpoint_attr, from_cloud: bool):
        """Implementation of AttributeListener interface

        This method is called if an attribute change comes from the cloud.
        """
        from thingsboard.endpoint.topicuuid import TopicUuid

        found_model_attribute = False
        model_attribute_name = None

        # Get the corresponding mapping
        for mod_attr_name, cl_att_mapping in self._attribute_mapping.items():
            if 'topic' in cl_att_mapping:
                if 'write' in cl_att_mapping['constraints']:
                    location_stack = self._location_stack_from_topic(cl_att_mapping['topic'])

                    # check attribute name
                    if endpoint_attr.get_name() == location_stack[0]:

                        # check all parents objects
                        compare_objects = True
                        endpoint_obj = endpoint_attr.get_parent()
                        if TopicUuid.EXTENDED_TOPIC:
                            for i in range(0, int((len(location_stack) - 2) / 2)):
                                if location_stack[2 + i * 2] != endpoint_obj.get_name():
                                    compare_objects = False # This is not the corresponding attribute we search
                                    break
                                endpoint_obj = endpoint_obj.get_parent_object_container()
                        else:
                            for i in range(0, int((len(location_stack) - 1))):
                                if location_stack[1 + i] != endpoint_obj.get_name():
                                    compare_objects = False # This is not the corresponding attribute we search
                                    break
                                endpoint_obj = endpoint_obj.get_parent_object_container()

                        if compare_objects:
                            # We found the right attribute. Leave the for loop here
                            model_attribute_name = mod_attr_name
                            # endpoint_attribute_mapping = cl_att_mapping
                            break

            else:
                if cl_att_mapping['objectName'] == endpoint_attr.get_parent().get_name() and \
                        cl_att_mapping['attributeName'] == endpoint_attr.get_name() and \
                        'write' in cl_att_mapping['constraints']:
                    model_attribute_name = mod_attr_name
                    # endpoint_attribute_mapping = cl_att_mapping
                    break

        # Leave if nothing found
        if model_attribute_name is None:
            return found_model_attribute

        # Strategy:
        # 1. Try to call method 'on_attribute_set_from_cloud(attribute_name, endpoint_attr)'
        # 2. Search method with 'set_<attribute-name>_from_cloud(value)
        # 3. Search method with same name
        # 4. Search setter method of attribute (ex.: set_power(value) or setPower(value))
        # 5. Search the attribute and access it directly

        # Try call method 'on_attribute_set_from_cloud(attribute_name, endpoint_attr)'
        if not found_model_attribute:
            general_callback_method_name = 'on_attribute_set_from_cloud'
            if hasattr(self, general_callback_method_name):
                method = getattr(self, general_callback_method_name)
                if inspect.ismethod(method):
                    try:  # Try to call the method. Maybe it fails because of wrong number of parameters
                        method(model_attribute_name, endpoint_attr)
                        found_model_attribute = True
                    except TypeError as type_error:
                        self.log.error(f'Exception : {type_error}')

        # Search method with 'on_<attribute-name>_set_from_cloud(value)
        if not found_model_attribute:
            specific_callback_method_name = 'on_' + model_attribute_name + '_set_from_cloud'
            if hasattr(self, specific_callback_method_name):
                method = getattr(self, specific_callback_method_name)
                if inspect.ismethod(method):
                    try:  # Try to call the method. Maybe it fails because of wrong number of parameters
                        method(endpoint_attr.get_value())
                        found_model_attribute = True
                    except TypeError as type_error:
                        self.log.error(f'Exception : {type_error}')

        # Check if provided name is already a method
        if not found_model_attribute:
            if hasattr(self, model_attribute_name):
                method = getattr(self, model_attribute_name)
                # Try to directly access it
                if inspect.ismethod(method):
                    try:  # Try to call the method. Maybe it fails because of wrong number of parameters
                        method(endpoint_attr.get_value())  # Call method and pass value by parameter
                        found_model_attribute = True
                    except Exception as e:
                        self.log.error(f'Exception : {e}')

        # Try to set attribute using setter method
        if not found_model_attribute:
            # Try to find a setter method
            set_method_names = attribute_helpers.generate_setters_from_attribute_name(model_attribute_name)

            for set_method_name in set_method_names:
                if hasattr(self, set_method_name):
                    method = getattr(self, set_method_name)
                    if inspect.ismethod(method):
                        try:
                            method(endpoint_attr.get_value())  # Call method with an pass value py parameter
                            found_model_attribute = True
                            break
                        except Exception as e:
                            self.log.error(f'Exception : {e}')

        # Try to set attribute by name
        if not found_model_attribute:
            attribute_names = attribute_helpers.generate_attribute_names_by_name(model_attribute_name)

            for attribute_name in attribute_names:
                if hasattr(self, attribute_name):
                    if hasattr(self, attribute_name):
                        attr = getattr(self, attribute_name)
                        # It should not be a method
                        if not inspect.ismethod(attr):
                            setattr(self, attribute_name, endpoint_attr.get_value())
                            found_model_attribute = True
                            break

        if not found_model_attribute:
            self.log.info(f'Did not find attribute for \'{endpoint_attr.get_name()}\'!')
        else:
            self.log.info('Endpoint @set attribute \'' + model_attribute_name + '\' to ' +
                          str(endpoint_attr.get_value()))

        return found_model_attribute

    def _update_endpoint_attribute(self, model_attribute_name, model_attribute_value, force=False):
        """Updates value of the attribute on the cloud.

        Only one thread should be responsible to call this method, means this
        method is not thread-safe.

        It might not be a good idea to call this method using the thread serving the MQTT
        client connection!
        """
        assert not inspect.ismethod(model_attribute_value), 'Value must be of standard type!'

        if (self.has_valid_data() or force) and self._endpoint_node:
            if model_attribute_name in self._attribute_mapping:
                # Get endpoint mapping for the model attribute
                endpoint_attribute_mapping = self._attribute_mapping[model_attribute_name]

                location_stack = []

                if 'topic' in endpoint_attribute_mapping and endpoint_attribute_mapping['topic']:
                    location_stack = self._location_stack_from_topic(endpoint_attribute_mapping['topic'])
                else:
                    if 'attributeName' in endpoint_attribute_mapping:
                        # Construct the location stack (inverse topic structure)
                        location_stack = [endpoint_attribute_mapping['attributeName'], 'attributes',
                                          endpoint_attribute_mapping['objectName'], 'objects']

                if location_stack:
                    if 'toEndpointAttributeValueConverter' in endpoint_attribute_mapping:
                        model_attribute_value = endpoint_attribute_mapping['toEndpointAttributeValueConverter'](
                            model_attribute_value)

                    endpoint_attribute_object = None

                    # Get endpoint attribute
                    endpoint_attribute_object = self._endpoint_node.find_attribute(location_stack)

                    if endpoint_attribute_object:
                        # Update only if force is true or model attribute value is different from that in the cloud
                        if force is True or model_attribute_value != endpoint_attribute_object.get_value():
                            if 'read' in endpoint_attribute_mapping['constraints']:
                                endpoint_attribute_object.set_value(model_attribute_value)  # Set the new value on the cloud
                    else:
                        self.log.warning(f'Did not find endpoint attribute for \'{model_attribute_name}\' model attribute!')
            else:
                self.log.warning(f'Did not find endpoint mapping for model attribute \'{model_attribute_name}\'!')

    def _update_endpoint_attributes(self, model=None, force=True):
        """Updates all endpoint attributes which where changed in model.

        In case the parameter force is set to true, the update to the cloud is forced.
        """
        if self.has_valid_data() and self._endpoint_node and self._attribute_mapping:
            model = model if model is not None else self

            for model_attribute_name, endpoint_attribute_mapping in self._attribute_mapping.items():
                # Only update attributes with 'read' or 'static' constraints
                if 'read' in endpoint_attribute_mapping['constraints'] or 'static' in \
                        endpoint_attribute_mapping['constraints']:
                    try:
                        attribute_value = getattr(model, model_attribute_name)
                        # Update attribute in the cloud
                        self._update_endpoint_attribute(model_attribute_name, attribute_value, force)
                    except Exception:
                        self.log.warning(f'Attribute \'{model_attribute_name}\' in model not found!')

    def _force_update_of_endpoint_attributes(self, model=None):
        """Forces updated of endpoint attributes.

        It is made only to get fluent graphs on visualisation applications.
        """
        self._update_endpoint_attributes(model=model, force=True)

    def has_valid_data(self) -> bool:
        """Returns true if model object has valid data.

        Reimplement this method in derived class to change the behavior

        Default implementation returns always true.
        """
        return True
