# -*- coding: utf-8 -*-

import logging
import os
import ssl
import tb_device_mqtt as mqtt
import paho.mqtt.client as paho
from datetime import datetime
from threading import RLock


class MqttClient(object):
    """Proxy class providing the old call API to connect to the ThingsBoard MQTT client.
    """

    # Errors from mqtt module - mirrored into this class
    MQTT_ERR_SUCCESS = paho.MQTT_ERR_SUCCESS
    MQTT_ERR_NO_CONN = paho.MQTT_ERR_NO_CONN
    MQTT_ERR_INVAL = paho.MQTT_ERR_INVAL

    log = logging.getLogger('thingsboard.mqttclient')

    def __init__(self, host, client_id='', clean_session=True, options=None):
        super(MqttClient, self).__init__()
        self._host = host
        self._on_connect_callback = None
        self._on_connected_callback = None
        self._on_disconnect_callback = None
        self._on_message_published_callback = None
        self._on_shared_attributes_changed_callback = None
        self._client = None                 # type: mqtt.TBDeviceMqttClient or None
        self._client_lock = RLock()  # Protects access to _client attribute

        # Store mqtt client parameter for potential later reconnection
        self._client_client_id = client_id
        self._client_clean_session = clean_session

        self._options = options

    def _create_mqtt_client(self, host, username, client_id='', clean_session=True):
        self._client_lock.acquire()
        if self._client is None:
            self._client = mqtt.TBDeviceMqttClient(host=host, username=username, client_id=client_id)

            #self._client.on_connect = self.on_connect
            #self._client.on_disconnect = self.on_disconnect
            #self._client.on_message = self.on_message
            #self._client.on_publish = self.on_published
        self._client_lock.release()

    def set_on_connect_callback(self, on_connect_callback):
        self._on_connect_callback = on_connect_callback

    def set_on_connected_callback(self, on_connected_callback):
        self._on_connected_callback = on_connected_callback

    def set_on_disconnect_callback(self, on_disconnect_callback):
        self._on_disconnect_callback = on_disconnect_callback

    def set_on_shared_attributes_changed_callback(self, on_shared_attributes_changed_callback):
        self._on_shared_attributes_changed_callback = on_shared_attributes_changed_callback

    def set_on_message_published(self, on_message_published_callback):
        self._on_message_published_callback = on_message_published_callback

    def start(self):
        self.connect(self._options)

    def connect(self, options):
        port = options.port if options.port else 1883  # Default port without ssl

        if options.ca_file:
            # Check if file exists
            if not os.path.isfile(options.ca_file):
                raise RuntimeError('CA file \'%s\' does not exist!' % options.ca_file)

        client_cert_file = None
        if options.client_cert_file:
            # Check if file exists
            if not os.path.isfile(options.client_cert_file):
                raise RuntimeError('Client certificate file \'%s\' does not exist!' % options.client_cert_file)
            else:
                client_cert_file = options.client_cert_file

        client_key_file = None
        if options.client_key_file:
            # Check if file exists
            if not os.path.isfile(options.client_key_file):
                raise RuntimeError('Client private key file \'%s\' does not exist!' % options.client_key_file)
            else:
                client_key_file = options.client_key_file

        # Check which TSL protocol version should be used
        try:
            tls_version = ssl.PROTOCOL_TLSv1_2
        except Exception:  # pragma: no cover
            tls_version = ssl.PROTOCOL_TLSv1  # pragma: no cover
        if options.tls_version:
            if options.tls_version.lower() in ('tlsv1', 'tlsv1.0'):
                tls_version = ssl.PROTOCOL_TLSv1

        self._client_lock.acquire()  # Protect _client attribute

        # Create MQTT client if necessary
        self._create_mqtt_client(host=self._host,
                                 username=options.username,
                                 client_id=self._client_client_id,
                                 clean_session=self._client_clean_session)

        if self._client:
            self._client.connect(callback=self.on_connect)

            # Subscribe to shared attribute changes
            self._client.subscribe_to_all_attributes(self._on_shared_attributes_changed_callback)
        return

        if options.will:
            self._client.will_set(options.will['topic'],
                                  options.will['message'],
                                  options.will['qos'],
                                  options.will['retained'])
        if self._client:
            if options.ca_file:
                port = options.port if options.port else 8883  # Default port with ssl
                self._client.tls_set(options.ca_file,  # CA certificate
                                     certfile=client_cert_file,  # Client certificate
                                     keyfile=client_key_file,  # Client private key
                                     tls_version=tls_version,  # ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_2
                                     ciphers=None)  # None, 'ALL', 'TLSv1.2', 'TLSv1.0'
                self._client.tls_insecure_set(True)  # True: No verification of the server hostname in
                # the server certificate
            else:
                self.log.error('No CA file provided. Connection attempt likely to fail!')

            # Check if username and password is provided
            if options.username:
                password = options.password
                if not options.password:
                    # paho client v1.3 and higher do no more accept '' as empty string. Need None
                    password = None
                self._client.username_pw_set(options.username, password=password)

            self._client_lock.release()  # Need to release lock before connect().
            # Otherwise other thread cannot disconnect

            # Let MQTT client do the connection
            self._client.connect(self._host, port=port)
            if self._client:
                self._client.loop_start()

    def disconnect(self, force_client_disconnect=True):
        """Disconnects MQTT client

        In case to let MQTT client die silently, call force_client_disconnect parameter with
        'false' value. In this case no disconnect callback method is called.

        ::param force_client_disconnect Set to true to call also MQTT clients disconnect method. Default: true
        :type force_client_disconnect bool
        :return None
        :rtype: None
        """
        self._client_lock.acquire()
        # Stop MQTT client if still running
        if self._client:
            if force_client_disconnect:
                self._client.on_disconnect = None  # Want get a disconnect callback call
                self._client.disconnect()
            self._client.stop()
            self._client = None

        self._client_lock.release()

    def stop(self):
        self.disconnect()

    def is_connected(self):
        return self._client and self._client.is_connected()

    def on_connect(self, client, userdata, flags, result_code, *extra_params):
        if result_code == 0:
            self.log.info('Connection to ThingsBoard MQTT broker established')
            if self._on_connect_callback:
                self._on_connect_callback()
            if self._on_connected_callback:
                self._on_connected_callback()
        else:
            if result_code == 1:
                self.log.error('Connection refused - incorrect protocol version')
            elif result_code == 2:
                self.log.error('Connection refused - invalid client identifier')
            elif result_code == 3:
                self.log.error('Connection refused - server unavailable')
            elif result_code == 4:
                self.log.error('Connection refused - bad username or password')
            elif result_code == 5:
                self.log.error('Connection refused - not authorised')
            else:
                self.log.error('Connection refused - unknown reason')

    def on_disconnect(self, client, userdata, rc):
        self.log.info('Disconnect: %d' % rc)

        # Caution:
        # Do not call self.disconnect() here. It will kill the _thread calling this
        # method and any subsequent code will not be executed!
        # self.disconnect()

        # Notify container class if disconnect callback
        # was registered.
        if self._on_disconnect_callback:
            self._on_disconnect_callback(rc)
        else:
            self.log.warning('On disconnect callback not set')

    def on_published(self, client, userdata, mid):
        # print('Msg #{} sent'.format(mid))

        # Notify container class
        if self._on_message_published_callback:
            self._on_message_published_callback(client, userdata, mid)

    def publish(self, topic, payload=None, qos=0, retain=False):

        if not self.is_connected():
            message_info = paho.MQTTMessageInfo(mid=0)
            message_info.rc = self.MQTT_ERR_INVAL
            return message_info

        message_info = self._client.publish(topic, payload, qos, retain)
        return message_info

    def subscribe(self, topic, qos=0):
        if self._client:
            return self._client.subscribe(topic, qos)
        else:
            return self.MQTT_ERR_NO_CONN, None

    def send_telemetry(self, telemetry: dict, timestamp: datetime = None, queued: bool = True):
        return self._client.send_telemetry(telemetry, timestamp, queued)

    def send_attributes(self, attributes, quality_of_service=None, wait_for_publish=True):
        return self._client.send_attributes(attributes, quality_of_service, wait_for_publish)

    def request_attributes(self, client_keys=None, shared_keys=None, callback=None):
        return self._client.request_attributes(client_keys, shared_keys, callback)


class MqttConnectOptions(object):
    def __init__(self):
        self.port = 8883  # Default port with ssl
        self.username = ''
        self.password = ''
        self.ca_file = None  # type: str or None
        self.client_cert_file = None  # type: str or None
        self.client_key_file = None  # type: str or None
        self.tls_version = None  # type: str or None
        self.will = None  # type dict

    def set_will(self, topic, message, qos, retained):
        self.will = {
            'topic': topic,
            'message': message,
            'qos': qos,
            'retained': retained
        }
