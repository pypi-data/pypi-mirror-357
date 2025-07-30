# -*- coding: utf-8 -*-

import os
import uuid
from abc import ABCMeta
from thingsboard.common.utils import path_helpers
from .pending_update import PendingUpdate


class MqttClientPersistence(object):
    """Mimic the behavior of the java.MqttClientPersistence interface.

    Compatible with MQTT v3.

    See: https://www.eclipse.org/paho/files/javadoc/org/eclipse/paho/client/mqttv3/MqttClientPersistence.html
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def clear(self):
        """Clears persistence, so that it no longer contains any persisted data.
        """
        raise NotImplementedError

    def close(self):
        """Close the persistent store that was previously opened.
        """
        raise NotImplementedError

    def contains_key(self, key):
        """Returns whether or not data is persisted using the specified key.

        :param key The key for data, which was used when originally saving it.
        :type key str
        :return True if key is present.
        """
        raise NotImplementedError

    def get(self, key):
        """Gets the specified data out of the persistent store.

        :param key The key for the data to be removed from the store.
        :type key str
        :return The wanted data.
        """
        raise NotImplementedError

    def keys(self):
        """Returns an Enumeration over the keys in this persistent data store.

        :return: generator
        """
        raise NotImplementedError

    def open(self, client_id, server_uri):
        """Initialise the persistent store.

        Initialise the persistent store. If a persistent store exists for this client ID then open it,
        otherwise create a new one. If the persistent store is already open then just return. An application
        may use the same client ID to connect to many different servers, so the client ID in conjunction
        with the connection will uniquely identify the persistence store required.

        :param client_id The client for which the persistent store should be opened.
        :type client_id str
        :param server_uri The connection string as specified when the MQTT client instance was created.
        :type server_uri str
        """
        raise NotImplementedError

    def put(self, key, persistable):
        """Puts the specified data into the persistent store.

        :param key The key for the data, which will be used later to retrieve it.
        :type key str
        :param persistable The data to persist.
        :type persistable bool
        """
        raise NotImplementedError

    def remove(self, key):
        """Remove the data for the specified key.

        :param key The key associated to the data to remove.
        :type key str
        :return None
        """
        raise NotImplementedError


class MqttMemoryPersistence(MqttClientPersistence):
    """Persistence store that uses memory.
    """

    def __init__(self):
        super(MqttMemoryPersistence, self).__init__()
        self._persistence = {}

    def open(self, client_id, server_uri):
        pass

    def close(self):
        self.clear()

    def put(self, key, persistable):
        self._persistence[key] = persistable

    def get(self, key):
        if key in self._persistence:
            return self._persistence[key]
        return None

    def contains_key(self, key):
        return True if key in self._persistence else False

    def keys(self):
        keys = []
        for key in self._persistence.keys():
            keys.append(key)
        return keys

    def remove(self, key):
        # Remove the key if it exist. If it does not exist
        # leave silently
        self._persistence.pop(key, None)

    def clear(self):
        self._persistence.clear()


class MqttDefaultFilePersistence(MqttClientPersistence):
    """Persistence store providing file based storage.
    """

    DEFAULT_DIRECTORY = '~/mqtt-persistence'

    def __init__(self, directory=None):
        """
        :param directory: Base directory where to store the persistent data
        """
        super(MqttDefaultFilePersistence, self).__init__()

        if directory is None or directory == '':
            directory = self.DEFAULT_DIRECTORY

        self._directory = path_helpers.prettify(directory)
        self._per_client_id_and_server_uri_directory = None  # type: str or None

        # Give a temporary unique storage name in case open() method does not get called
        self._per_client_id_and_server_uri_directory = str(uuid.uuid4())

        # Create base directory
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

    def open(self, client_id, server_uri):
        """Initialises the persistent store.

        :param client_id: MQTT client id
        :type client_id: str
        :param server_uri: Connection name to the server
        :type server_uri: str
        """
        self._per_client_id_and_server_uri_directory = client_id + '-' + server_uri

        # Remove some unwanted characters in sub-directory name
        self._per_client_id_and_server_uri_directory = self._per_client_id_and_server_uri_directory.replace('/', '')
        self._per_client_id_and_server_uri_directory = self._per_client_id_and_server_uri_directory.replace('\\', '')
        self._per_client_id_and_server_uri_directory = self._per_client_id_and_server_uri_directory.replace(':', '')
        self._per_client_id_and_server_uri_directory = self._per_client_id_and_server_uri_directory.replace(' ', '')

        # Create storage directory
        if not os.path.exists(self._storage_directory()):
            os.makedirs(self._storage_directory())

    def _storage_directory(self):
        return os.path.join(self._directory, self._per_client_id_and_server_uri_directory)

    def _key_file_name(self, key):
        return os.path.join(self._storage_directory(), key)

    def close(self):
        pass

    def put(self, key, persistable):
        """

        :param key:
        :param persistable:
        :type persistable: str or PendingUpdate
        :return:
        """

        # Convert string to PendingUpdate
        if isinstance(persistable, str):
            persistable = PendingUpdate(persistable)

        with open(self._key_file_name(key), mode='w') as file:
            # File is opened in binary mode. So bytes need to be stored
            # Convert str -> bytes
            file.write(persistable.get_data())

    def get(self, key):
        if os.path.exists(self._key_file_name(key)):
            with open(self._key_file_name(key), mode='r') as storage_file:
                return PendingUpdate(storage_file.read())
        return None

    def contains_key(self, key):
        return True if os.path.exists(self._key_file_name(key)) else False

    def keys(self):
        keys = next(os.walk(self._storage_directory()))[2]
        return keys

    def remove(self, key):
        # Remove the key if it exist. If it does not exist
        # leave silently
        key_file_name = self._key_file_name(key)
        try:
            if os.path.isfile(key_file_name):
                os.remove(key_file_name)
        except Exception:  # pragma: no cover
            pass  # pragma: no cover

    def clear(self):
        for key in os.listdir(self._storage_directory()):
            key_file_name = self._key_file_name(key)
            if os.path.isfile(key_file_name):
                os.remove(key_file_name)
