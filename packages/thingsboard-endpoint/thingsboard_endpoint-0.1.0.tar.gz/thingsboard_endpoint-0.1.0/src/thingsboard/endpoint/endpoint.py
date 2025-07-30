#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os
from dataclasses import dataclass

from tb_device_mqtt import TBPublishInfo

import thingsboard.endpoint.mqtt as mqtt
import thingsboard.common.utils.timestamp_helpers as TimeStampProvider
import time
from thingsboard.common.core.threaded import Threaded
from thingsboard.common.utils import path_helpers
from thingsboard.common.utils.resource_loader import ResourceLoader
from thingsboard.endpoint.exception.modification_exception import ModificationException
from thingsboard.endpoint.exception.invalid_property_exception import InvalidPropertyException
from thingsboard.endpoint.interface.message_format import MessageFormat
from thingsboard.endpoint.interface.node_container import NodeContainer
from thingsboard.endpoint.message_format.factory import MessageFormatFactory
from thingsboard.endpoint.message_format.json_format import JsonMessageFormat
from thingsboard.endpoint.message_format.thingsboard_format import ThingsboardMessageFormat
from thingsboard.endpoint.properties_endpoint_configuration import PropertiesEndpointConfiguration
from thingsboard.endpoint.topicuuid import TopicUuid
import paho.mqtt.client as paho

version = ''
# Get endpoint python version info from init file
with open(os.path.dirname(os.path.realpath(__file__)) + '/version.py') as vf:
    content = vf.readlines()
    for line in content:
        if '__version__' in line:
            values = line.split('=')
            version = values[1]
            version = version.strip('\n')
            version = version.strip('\r')
            version = version.replace('\'', '')
            version = version.strip(' ')
            break


@dataclass
class MqttMessage:
    """Data structure used internally by Endpoint class.
    """
    topic: str
    payload: str
    timestamp: int = 0  # Time in milliseconds
    qos: int = 1
    retain: bool = False


class Endpoint(Threaded, NodeContainer):
    """The ThingsBoard endpoint. Used by the device to represent itself in the cloud.

    Contains among other things the mqtt client to talk to the MQTT broker.
    """

    # Constants ######################################################################################
    MQTT_HOST_URI_PROPERTY = 'host'
    MQTT_PERSISTENCE_MEMORY = 'memory'
    MQTT_PERSISTENCE_FILE = 'file'
    MQTT_PERSISTENCE_NONE = 'none'
    MQTT_PERSISTENCE_PROPERTY = 'thingsboard.endpoint.persistence'
    MQTT_PERSISTENCE_DEFAULT = MQTT_PERSISTENCE_FILE
    MQTT_PERSISTENCE_LOCATION = 'thingsboard.endpoint.persistenceLocation'

    THINGSBOARD_SERVER_CERT_FILE_PROPERTY = 'thingsboard.server.tls.cert'
    ENDPOINT_IDENTITY_TLS_VERSION_PROPERTY = 'thingsboard.endpoint.tls.version'  # tlsv1.2
    ENDPOINT_IDENTITY_CERT_FILE_PROPERTY = 'thingsboard.endpoint.tls.cert'  # (*.pem)
    ENDPOINT_IDENTITY_KEY_FILE_PROPERTY = 'thingsboard.endpoint.tls.key'  # (*.pem)

    log = logging.getLogger(__name__)

    def __init__(self, uuid, configuration=None, locations: str or list = None):
        super(Endpoint, self).__init__()

        from thingsboard.endpoint.node import Node

        self._end_point_is_ready = False  # Set to true after connection and subscription

        self.uuid = uuid  # type: str
        self.nodes = {}  # type: dict[Node]
        self.clean_session = True
        self.message_format = None  # type: MessageFormat or None
        self.persistence = None  # type: MqttClientPersistence or None
        self._publish_message = list()  # type: list[MqttMessage]
        self._received_message = list()  # type: list[dict]

        # Used for debug/testing purpose only
        self._published_not_acknowledged_message = dict()  # type: dict[mqtt.MQTTMessageInfo]
        self._published_not_acknowledged_high_water_mark = 0

        self.log.debug('Creating Endpoint %s' % uuid)

        # Check if a configuration with properties is given
        if configuration is None:
            properties_file = self.uuid + '.properties'
            ext_locations = ['home:' + '/.config/thingsboard/', 'file:/etc/thingsboard/']
            if locations:
                if isinstance(locations, str):
                    ext_locations = [locations, ] + ext_locations
                else:
                    ext_locations = locations + ext_locations

            # Try to load properties using a config file
            properties = ResourceLoader.load_from_locations(properties_file,
                                                            ext_locations)
            if properties:
                configuration = PropertiesEndpointConfiguration(properties)
            else:
                message = 'Could not find properties file \'' + properties_file + '\' in the following locations:\n'
                for location in ext_locations:
                    message += ' - ' + location + '\n'
                exit(message)

        self._retry_interval = 10  # Connect retry interval in seconds
        self.message_format = ThingsboardMessageFormat()

        # Check if 'host' property is present in config file
        host = configuration.get_property(self.MQTT_HOST_URI_PROPERTY)
        if host == '':
            exit('Missing mandatory property "' + self.MQTT_HOST_URI_PROPERTY + '"')

        # Create persistence object.
        persistence_type = configuration.get_property(self.MQTT_PERSISTENCE_PROPERTY, self.MQTT_PERSISTENCE_DEFAULT)
        if persistence_type == self.MQTT_PERSISTENCE_MEMORY:
            self.persistence = mqtt.MqttMemoryPersistence()
        elif persistence_type == self.MQTT_PERSISTENCE_FILE:
            persistence_location = configuration.get_property(self.MQTT_PERSISTENCE_LOCATION)
            self.persistence = mqtt.MqttDefaultFilePersistence(directory=persistence_location)
        elif persistence_type == self.MQTT_PERSISTENCE_NONE:
            self.persistence = None
        else:
            raise InvalidPropertyException('Unknown persistence implementation ' +
                                           '(endpoint.persistence): ' +
                                           '\'' + persistence_type + '\'')
        # Open persistence storage
        if self.persistence:
            self.persistence.open(client_id=self.uuid, server_uri=host)

        self.options = mqtt.MqttConnectOptions()

        # Last will is a message with the UUID of the endpoint and no payload.
        will_message = 'DEAD'
        self.options.set_will('@offline/' + uuid, will_message, 1, False)

        self.options.ca_file = configuration.get_property(self.THINGSBOARD_SERVER_CERT_FILE_PROPERTY, None)
        self.options.client_cert_file = configuration.get_property(self.ENDPOINT_IDENTITY_CERT_FILE_PROPERTY, None)
        self.options.client_key_file = configuration.get_property(self.ENDPOINT_IDENTITY_KEY_FILE_PROPERTY, None)
        if configuration.contains_key('device-access-token'):
            self.options.username = configuration.get_property('device-access-token')
        else:
            self.options.username = configuration.get_property('username')
        self.options.password = configuration.get_property('password')
        self.options.tls_version = configuration.get_property(self.ENDPOINT_IDENTITY_TLS_VERSION_PROPERTY, 'tlsv1.2')

        # Make path usable
        self.options.ca_file = path_helpers.prettify(self.options.ca_file)
        self.options.client_cert_file = path_helpers.prettify(self.options.client_cert_file)
        self.options.client_key_file = path_helpers.prettify(self.options.client_key_file)

        self._client = mqtt.MqttClient(host,
                                       client_id=self.uuid + '-endpoint-',
                                       clean_session=self.clean_session,
                                       options=self.options)
        # Register callback method for connection established
        self._client.set_on_connected_callback(self._on_connected)
        # Register callback method to be called when shared attributes change in the cloud
        self._client.set_on_shared_attributes_changed_callback(self._on_shared_attributes_changed)
        # Register callback method to get notified after message was published (received by the MQTT broker)
        self._client.set_on_message_published(self._on_message_published)
        # Start MQTT client
        self._client.start()

        # Setup and start internal _thread
        self.setup_thread(name=uuid)
        self.start_thread()

    def _run(self):
        while self._thread_should_run:

            self._process_received_messages()
            self._process_publish_messages()

            self._check_published_not_acknowledged_container()
            self._check_persistent_data_store()

            # Wait until next interval begins
            if self._thread_should_run:
                self._thread_sleep_interval()

        self._thread_left_run_loop = True

    def close(self):
        # Stop Mqtt client
        self._client.stop()

    def _publish(self, topic: str, payload: str, timestamp=0, qos=1, retain=False):
        """Publish a message to the cloud.

        The message is pushed onto a queue to free the calling thread. The message is then send by the
        internal thread as soon as possible.

        :param topic: Contains the action and the internal representation of the endpoint attribute. Used to
                      construct the key for the telemetry or the ThingsBoard attribute.
        :param payload: A json string representing the endpoint attribute. The json structure must contain at least
                        contain the entry 'value' and 'constraint'. The entry 'timestamp' is optional.
        """

        if timestamp == 0:
            timestamp = TimeStampProvider.get_time_in_milliseconds()

        msg = MqttMessage(topic, payload, timestamp=timestamp, qos=qos, retain=retain)
        self._publish_message.append(msg)

        # Wake up endpoint _thread. It will publish the queued message. See _process_publish_messages()
        self.wakeup_thread()

    def _process_publish_messages(self):
        """Processes message ready to be sent to cloud.

        In case the MQTT broker is not available, the messages are stored in the
        persistent data store.
        """

        # Delay message publishing if there is no connection to ThingsBoard
        if not self._client.is_connected():
            # Push waiting messages into persistence data store
            while len(self._publish_message):
                msg = self._publish_message.pop(0)
                self._put_persistent_data_store(msg.topic, msg.payload, msg.timestamp)
            return

        while len(self._publish_message):

            # Do not pop any messages if there is no connection to ThingsBoard
            if not self._client.is_connected():
                return

            # Get next message
            msg = self._publish_message.pop(0)

            tb_publish_info = self._send_message_to_thingsboard_server(msg)

            if tb_publish_info.rc() == TBPublishInfo.TB_ERR_SUCCESS:
                pass
            else:
                self._put_persistent_data_store(msg.topic, msg.payload, msg.timestamp)

            # Publish message via the MQTT client
            #message_info = self._client.publish(msg.topic, msg.payload, msg.qos, msg.retain)

            #if message_info.rc == self._client.MQTT_ERR_SUCCESS:
            #    # Add message to published (but not acknowledged) messages
            #    self._published_not_acknowledged_message[message_info.mid] = msg
            #else:
            #    # Could not transmit. Add it to data store
            #    self._put_persistent_data_store(msg.topic, msg.payload, msg.timestamp)

    def _send_message_to_thingsboard_server(self, msg: MqttMessage) -> TBPublishInfo:
        result = TBPublishInfo(paho.MQTTMessageInfo(None))
        if msg.topic[:7].lower() == '@update':
            node_topic = self.extract_node_topic(msg.topic)

            payload_data = json.loads(msg.payload)

            if payload_data['constraint'].lower() == 'measure':
                telemetry = {
                    'ts' : int(payload_data.get('timestamp') * 1000) if 'timestamp' in payload_data else msg.timestamp,
                    'values' : {}
                }

                if 'value' in payload_data:
                    telemetry['values'][node_topic] = payload_data.get('value')

                result = self._client.send_telemetry(telemetry)
            else:
                attribute = {
                    node_topic : payload_data.get('value')
                }
                result = self._client.send_attributes(attribute)
        elif msg.topic[:10].lower() == '@nodeadded':
            attribute = {
                msg.topic: msg.payload
            }
            result = self._client.send_attributes(attribute)
        else:
            self.log.info('Unrecognized topic: ' + msg.topic)
            result = self._client.send_attributes({ msg.topic: msg.payload })
        return result


    def _check_published_not_acknowledged_container(self):
        msg_count = len(self._published_not_acknowledged_message)
        if msg_count > 0:
            self._published_not_acknowledged_high_water_mark = max(self._published_not_acknowledged_high_water_mark,
                                                                   msg_count)
            # if msg_count > 1:
            #     print('Not published messages: {} (max: {})'.format(msg_count,
            #                                                        self._published_not_acknowledged_high_water_mark))

    def _on_attributes_response(self, content, msg):
        # Called by the MQTT client _thread!

        # print(f'Attributes response: {content}')

        self._received_message.append({'content': content, 'msg': msg})
        # Tell endpoint _thread it can process a message
        self.wakeup_thread()

    def _on_shared_attributes_changed(self, content, msg):
        # Called by the MQTT client _thread!

        # print(f'Shared attributes changed: {content}')

        self._received_message.append({'content': content, 'msg': msg})
        # Tell endpoint _thread it can process a message
        self.wakeup_thread()

    def _process_received_messages(self):
        while len(self._received_message):
            msg_data = self._received_message.pop(0)
            self._process_received_message(msg_data)

    def _process_received_message(self, msg_data):
        try:
            # Need to convert from bytes to string
            payload = json.dumps(msg_data['content'])

            # First determine the message format (first byte identifies the message format).
            message_format = MessageFormatFactory.message_format(payload[0])
            if message_format is None:
                self.log.error('Message-format ' + payload + " not supported!")
                return

            # Check if it's a 'request attributes' response containing 'shared' attributes
            if 'shared' in msg_data['content']:
                for update_info in msg_data['content']['shared'].items():
                    topic = update_info[0]
                    payload = json.dumps({topic: update_info[1]})
                    self._attribute_update(topic, payload, message_format=message_format)

            # Check if it's a 'request attributes' response containing 'client' attributes
            if 'client' in msg_data['content']:
                for update_info in msg_data['content']['client'].items():
                    topic = update_info[0]
                    payload = json.dumps({topic: update_info[1]})
                    self._attribute_update(topic, payload, message_format=message_format)

            # Check for shared attribute changed on server. Comes directly with {key, value}
            if 'shared' not in msg_data['content'] and 'client' not in msg_data['content']:
                # Extract key from first element. It's the topic
                topic = next(iter(msg_data['content']))
                self._attribute_update(topic, payload, message_format=message_format)
        except Exception as exception:
            self.log.error(exception, exc_info=True)

    def _on_message_published(self, client, userdata, mid):
        # Called by the MQTT client _thread!

        # if mid % 100 == 0:
            # print('Msg #{} sent'.format(mid))

        # Remove the sent message from the list
        if mid in self._published_not_acknowledged_message:
            del self._published_not_acknowledged_message[mid]
        else:
            # print('Warning: #{} not in published msgs!'.format(mid))
            pass

        msg_count = len(self._published_not_acknowledged_message)
        if msg_count > 0:
            self._published_not_acknowledged_high_water_mark = max(self._published_not_acknowledged_high_water_mark,
                                                                   msg_count)

    def subscribe_to_set_commands(self):
        (result, mid) = self._client.subscribe('@set/' + self.get_uuid().to_string() + '/#', 1)
        return True if result == self._client.MQTT_ERR_SUCCESS else False

    def request_attributes(self, client_keys=None, shared_keys=None, callback=None):
        if callback is None:
            callback = self._on_attributes_response
        self._client.request_attributes(client_keys, shared_keys, callback)

    def add_node(self, node_name, cls_or_object):
        from thingsboard.endpoint.node import Node

        if node_name != '' and cls_or_object is not None:
            node = None

            self.log.debug('Adding node %s' % node_name)

            # Add node to endpoint
            if isinstance(cls_or_object, Node):
                node = cls_or_object
                pass  # All right. We have the needed object
            else:
                raise RuntimeError('Wrong object type')

            if node:
                # We got an object
                node.set_name(node_name)
                node.set_parent_node_container(self)

                assert not node_name in self.nodes, 'Node with given name already present!'
                self.nodes[node_name] = node

                # If the endpoint is online, send node add message
                if self.is_online():
                    data = self.message_format.serialize_node(node)
                    self._publish('@nodeAdded/' + node.get_uuid().to_string(), data)
                else:
                    self.log.info('Not sending \'@nodeAdded\' message. No connection to broker!')

    def get_node(self, node_name):
        """Returns the node identified by the given name
        :param node_name The Name of the node
        :type node_name str
        """
        return self.nodes.get(node_name, None)

    def _attribute_update(self, topic, payload, message_format=None):
        topic_levels = self.get_topic_levels(topic)
        # Create attribute location path stack.
        location = []
        for topicLevel in topic_levels:
            location.insert(0, topicLevel)

        # Read the action tag from the topic
        action = topic_levels[0]
        if action == 'set':
            location.pop()
            self._set(topic, location, message_format, payload)
        else:
            self.log.error('Method \"' + action + '\" not supported!')

    def _set(self, topic, location, message_format, data):
        """Assigns a new value to a attribute.

        :param topic: Topic representing the attribute
        :param location: Location stack
        :type location list
        :param message_format: Message format according to the data parameter
        :param data: Contains among other things the value to be assigned
        :return:
        """

        # Get the node with the name according to the topic
        node = self.nodes.get(location[-1])
        if node:
            location.pop()
            # Get the attribute reference
            attribute = node.find_attribute(location)
            if attribute:
                # Deserialize the message into the attribute
                message_format.deserialize_attribute(data, attribute)
            else:
                self.log.error('Attribute \"' + location[0] + '\" in node \"' + node.get_name() + '\" not found!')
        else:
            self.log.error('Node \"' + location.pop() + '\" not found!')

    ######################################################################
    # Interface implementations
    #
    def get_uuid(self):
        return TopicUuid(self)

    def get_name(self):
        return self.uuid

    def set_name(self, name):
        raise ModificationException('Endpoint name can not be changed!')

    def attribute_has_changed_by_endpoint(self, attribute):
        """
        :param attribute:
        :type attribute: Attribute
        """

        try:
            # Create the MQTT message using the given message format.
            topic = '@update/' + attribute.get_uuid().to_string()
            payload = self.message_format.serialize_attribute(attribute)

            self._publish(topic, payload, timestamp=attribute.get_timestamp())
        except Exception as exception:
            self.log.error(exception, exc_info=True)

    def attribute_has_changed_by_cloud(self, attribute):
        """Informs the endpoint that an underlying attribute has changed (initiated from the cloud).

        Attribute changes initiated from the cloud (@set) are directly received
        by the concerning attribute. The attribute forwards the information
        up to the parents till the endpoint.
        """
        pass

    def _on_connected(self):
        """This callback is called after the MQTT client has successfully connected to the broker.
        """
        # Announce our presence to the broker
        # self.announce()
        # It is too early here because the endpoint model
        # is not loaded at this moment

        #success = self.subscribe_to_set_commands()
        #if not success:
        #    self.log.critical('Could not subscribe to @set topic!')

        # Try to send stored messages to the cloud
        # self._purge_persistent_data_store()
        # It may not be a good idea to send this data to the cloud using
        # the connection _thread!

        self._end_point_is_ready = True

        # time.sleep(4)  # Give the clients time to connect to broker and to set up the mqtt queue

    def _on_connection_thread_finished(self):
        self.log.info('Connection _thread finished')
        self.thread = None

    def is_online(self):
        return self._client.is_connected() and self._end_point_is_ready

    def wait_until_online(self):
        while not self.is_online():
            time.sleep(0.2)

    def announce(self):
        # Send birth message
        self.log.info('Sending birth message...')
        str_message = self.message_format.serialize_endpoint(self)
        self._publish('@online/' + self.uuid, str_message, retain=True)

    @staticmethod
    def get_action(topic: str) -> str:
        """Extracts the action from a topic.

        Ex. topic: '@update/CrazyFrogEndpoint/nodes/CrazyFrog/objects/properties/attributes/_sinus'
        returns '@update'
        """
        topic_levels = topic.split('/')

        # Read the action tag from the topic
        action = topic_levels[0]
        return action

    @staticmethod
    def extract_node_topic(topic: str) -> str:
        """Extracts the remaining topic after the endpoint name.

        Removes the action and endpoint name and returns the remaining topic
        Ex. topic: '@update/CrazyFrogEndpoint/nodes/CrazyFrog/objects/properties/attributes/_sinus'
        returns 'nodes/CrazyFrog/objects/properties/attributes/_sinus'
        """
        topic_levels = topic.split('/')
        node_topic = topic[len(topic_levels[0]) + len(topic_levels[1]) + 2:]
        return node_topic

    @staticmethod
    def get_topic_levels(topic: str) -> list[str]:
        """Breaks the topic into its pieces.
        """
        topic_levels = topic.split('/')
        return topic_levels

    def _check_persistent_data_store(self):
        # Check if there are messages in the persistence store
        if self.is_online() and self.persistence and len(self.persistence.keys()) > 0:
            # Try to send stored messages to cloud
            self._purge_persistent_data_store()

    def _put_persistent_data_store(self, topic, payload, timestamp):
        # If the message could not be sent for any reason, add the message to the pending
        # updates persistence if available.
        if self.persistence:
            if timestamp == 0:
                timestamp = TimeStampProvider.get_time_in_milliseconds()

            action = self.get_action(topic)
            topic_levels = self.get_topic_levels(topic)
            topic_levels.pop(0)  # Remove action

            try:
                if action == '@update':
                    msg_id = 'PendingUpdate-' + ';'.join(topic_levels) + '-' + str(int(timestamp))
                    self.persistence.put(msg_id, mqtt.PendingUpdate(payload))
                elif action == '@nodeAdded':
                    msg_id = 'PendingNodeAdded-' + ';'.join(topic_levels) + '-' + str(int(timestamp))
                    self.persistence.put(msg_id, mqtt.PendingUpdate(payload))
                else:
                    raise Exception('Unknown action type!')
            except Exception as exception:
                    self.log.error(exception, exc_info=True)

    def _purge_persistent_data_store(self):
        """Tries to send stored messages to cloud.
        """
        if self.persistence:
            print(str(len(self.persistence.keys())) + ' in persistence')

            action_map = {
                'PendingUpdate-': '@update',
                'PendingNodeAdded-': '@nodeAdded'}

            for key in self.persistence.keys():
                if self.is_online():
                    for pending_data_type, action in action_map.items():
                        # Check pending data type
                        if key.startswith(pending_data_type):
                            # Get the pending update persistent object from store
                            pending_update = self.persistence.get(key)

                            if pending_update is not None:
                                print('Copy pers: ' + key + ': ' + pending_update.get_data())

                                # Get the uuid of the endpoint
                                uuid = pending_update.get_uuid_from_persistence_key(key)

                                # Try to send the update to the broker and remove it from the storage
                                topic = action + '/' + uuid
                                self._publish(topic, pending_update.get_data())

                                # Remove key from store
                                self.persistence.remove(key)
                            break
                    time.sleep(0)  # Give other threads time to do its job
                else:
                    break


if __name__ == '__main__':
    pass
